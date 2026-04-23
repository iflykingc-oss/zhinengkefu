"""
增强的工作流调试功能
支持分模块调试、单步执行、断点等
"""
from typing import Dict, List, Optional, Any
from workflow.state import WorkflowState
from workflow.nodes import input_parser_node, knowledge_search_node, web_search_node, risk_assessment_node, answer_generation_node, feishu_notification_node
import logging
import json
import time

logger = logging.getLogger(__name__)


class WorkflowDebugger:
    """
    工作流调试器
    支持分模块调试、单步执行、断点等
    """

    def __init__(self):
        self.breakpoints = set()
        self.step_mode = False
        self.current_step = 0
        self.execution_history = []
        self.paused = False
        self.waiting_for_input = False

    def set_breakpoint(self, node_id: str):
        """设置断点"""
        self.breakpoints.add(node_id)
        logger.info(f"断点已设置在节点: {node_id}")

    def remove_breakpoint(self, node_id: str):
        """移除断点"""
        self.breakpoints.discard(node_id)
        logger.info(f"断点已移除: {node_id}")

    def enable_step_mode(self):
        """启用单步模式"""
        self.step_mode = True
        logger.info("单步模式已启用")

    def disable_step_mode(self):
        """禁用单步模式"""
        self.step_mode = False
        logger.info("单步模式已禁用")

    def pause(self):
        """暂停执行"""
        self.paused = True
        logger.info("工作流已暂停")

    def resume(self):
        """恢复执行"""
        self.paused = False
        logger.info("工作流已恢复")

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history

    def clear_history(self):
        """清空执行历史"""
        self.execution_history = []
        logger.info("执行历史已清空")


class EnhancedWorkflowRunner:
    """
    增强的工作流执行器
    支持调试、单步执行、断点等
    """

    def __init__(self, debugger: Optional[WorkflowDebugger] = None):
        self.debugger = debugger or WorkflowDebugger()
        self.nodes = {
            "input_parser": input_parser_node,
            "knowledge_search": knowledge_search_node,
            "web_search": web_search_node,
            "risk_assessment": risk_assessment_node,
            "answer_generation": answer_generation_node,
            "feishu_notification": feishu_notification_node
        }

    def execute_node(self, node_id: str, state: WorkflowState) -> WorkflowState:
        """
        执行单个节点

        Args:
            node_id: 节点ID
            state: 工作流状态

        Returns:
            更新后的状态
        """
        if node_id not in self.nodes:
            raise ValueError(f"未知的节点: {node_id}")

        # 记录执行开始
        start_time = time.time()
        node_function = self.nodes[node_id]

        logger.info(f"开始执行节点: {node_id}")

        # 检查断点
        if node_id in self.debugger.breakpoints:
            logger.warning(f"在断点处暂停: {node_id}")
            self.debugger.pause()
            # TODO: 等待用户输入

        # 检查是否暂停
        if self.debugger.paused:
            logger.info("工作流已暂停，等待恢复...")
            while self.debugger.paused:
                time.sleep(0.1)

        # 执行节点
        state = node_function(state)

        # 记录执行历史
        execution_time = time.time() - start_time
        self.debugger.execution_history.append({
            "node_id": node_id,
            "timestamp": time.time(),
            "execution_time": execution_time,
            "state_snapshot": {k: str(v)[:100] for k, v in state.items() if k != "messages"}
        })

        logger.info(f"节点执行完成: {node_id} (耗时: {execution_time:.3f}s)")

        return state

    def execute_workflow(self, initial_state: WorkflowState, node_order: List[str]) -> WorkflowState:
        """
        执行工作流

        Args:
            initial_state: 初始状态
            node_order: 节点执行顺序

        Returns:
            最终状态
        """
        state = initial_state

        for i, node_id in enumerate(node_order):
            logger.info(f"执行步骤 {i+1}/{len(node_order)}: {node_id}")
            state = self.execute_node(node_id, state)

            # 如果启用了单步模式，执行一个节点后暂停
            if self.debugger.step_mode and i < len(node_order) - 1:
                logger.info("单步模式：等待继续...")
                self.debugger.pause()
                while self.debugger.paused:
                    time.sleep(0.1)

        return state

    def execute_single_node(self, node_id: str, state: WorkflowState) -> WorkflowState:
        """
        执行单个节点（用于调试）

        Args:
            node_id: 节点ID
            state: 工作流状态

        Returns:
            更新后的状态
        """
        return self.execute_node(node_id, state)


class ModuleTester:
    """
    模块测试器
    用于单独测试每个节点
    """

    def __init__(self):
        self.runner = EnhancedWorkflowRunner()
        self.test_results = []

    def test_node(self, node_id: str, test_input: WorkflowState) -> Dict[str, Any]:
        """
        测试单个节点

        Args:
            node_id: 节点ID
            test_input: 测试输入

        Returns:
            测试结果
        """
        logger.info(f"开始测试节点: {node_id}")

        try:
            start_time = time.time()
            output = self.runner.execute_single_node(node_id, test_input.copy())
            execution_time = time.time() - start_time

            result = {
                "node_id": node_id,
                "status": "success",
                "execution_time": execution_time,
                "input": test_input,
                "output": output
            }

            self.test_results.append(result)
            logger.info(f"节点测试成功: {node_id} (耗时: {execution_time:.3f}s)")

            return result

        except Exception as e:
            logger.error(f"节点测试失败: {node_id} - {e}")
            result = {
                "node_id": node_id,
                "status": "error",
                "error": str(e),
                "input": test_input
            }
            self.test_results.append(result)
            return result

    def test_all_nodes(self, test_cases: Dict[str, WorkflowState]) -> Dict[str, Any]:
        """
        测试所有节点

        Args:
            test_cases: 测试用例（节点ID -> 测试输入）

        Returns:
            测试结果汇总
        """
        results = {}

        for node_id, test_input in test_cases.items():
            results[node_id] = self.test_node(node_id, test_input)

        return results

    def get_test_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        summary = {
            "total_tests": len(self.test_results),
            "success_count": sum(1 for r in self.test_results if r["status"] == "success"),
            "error_count": sum(1 for r in self.test_results if r["status"] == "error"),
            "total_time": sum(r.get("execution_time", 0) for r in self.test_results),
            "details": self.test_results
        }

        return summary


# 创建全局调试器实例
_global_debugger: Optional[WorkflowDebugger] = None


def get_global_debugger() -> WorkflowDebugger:
    """获取全局调试器"""
    global _global_debugger
    if _global_debugger is None:
        _global_debugger = WorkflowDebugger()
    return _global_debugger


def create_enhanced_workflow_runner() -> EnhancedWorkflowRunner:
    """创建增强的工作流执行器"""
    debugger = get_global_debugger()
    return EnhancedWorkflowRunner(debugger)


def create_module_tester() -> ModuleTester:
    """创建模块测试器"""
    return ModuleTester()
