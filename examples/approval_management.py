"""
AgentGuard SDK 审批功能示例

演示如何使用 ApprovalClient 提交审批理由和查询审批状态
"""
from agentguard_zhx import ApprovalClient

# 初始化审批客户端
approval_client = ApprovalClient(
    agentguard_url="http://localhost:8080",
    agent_api_key="ag_2a6d77701a734dffb93a3f68198f7db9"  # 替换为你的 API Key
)


def submit_approval_reason_example():
    """提交审批理由示例"""
    approval_id = "your_approval_id_here"  # 替换为实际的审批 ID
    reason = "需要删除该客户以清理测试数据，该客户为测试账号，不影响生产环境"

    print(f"提交审批理由...")
    print(f"审批ID: {approval_id}")
    print(f"理由: {reason}")

    try:
        result = approval_client.submit_reason(approval_id, reason)
        print(f"✓ 提交成功: {result}")
    except Exception as e:
        print(f"✗ 提交失败: {e}")


def query_approval_status_example():
    """查询审批状态示例"""
    approval_id = "your_approval_id_here"  # 替换为实际的审批 ID

    print(f"\n查询审批状态...")
    print(f"审批ID: {approval_id}")

    try:
        status_response = approval_client.get_status(approval_id)

        print(f"\n审批状态: {status_response.status.value}")

        if status_response.is_approved:
            print("✓ 审批已通过")
            if status_response.execution_result:
                print(f"执行结果: {status_response.execution_result}")
            else:
                print("等待执行中...")

        elif status_response.is_rejected:
            print(f"✗ 审批被拒绝")
            if status_response.remark:
                print(f"拒绝原因: {status_response.remark}")

        elif status_response.is_pending:
            print("⏳ 审批等待中")

        elif status_response.is_expired:
            print("⏰ 审批已过期")

    except Exception as e:
        print(f"✗ 查询失败: {e}")


def complete_approval_workflow_example():
    """完整的审批工作流示例"""
    print("=" * 60)
    print("完整审批工作流示例")
    print("=" * 60)

    # 假设这是从 LLM 响应中提取的审批 ID
    approval_id = "your_approval_id_here"

    # 步骤 1: 提交审批理由
    print("\n步骤 1: 提交审批理由")
    print("-" * 60)
    try:
        result = approval_client.submit_reason(
            approval_id,
            "用户请求删除测试客户数据，该操作已确认不会影响生产环境"
        )
        print(f"✓ 理由提交成功")
    except Exception as e:
        print(f"✗ 理由提交失败: {e}")
        return

    # 步骤 2: 等待用户通知审批通过
    print("\n步骤 2: 等待审批...")
    print("（在实际应用中，用户会在 AgentGuard 后台审批，然后告知 Agent）")

    # 步骤 3: 查询审批状态
    print("\n步骤 3: 查询审批状态")
    print("-" * 60)
    try:
        status_response = approval_client.get_status(approval_id)

        if status_response.is_approved and status_response.execution_result:
            print(f"✓ 审批通过并执行成功")
            print(f"执行结果: {status_response.execution_result}")
        elif status_response.is_pending:
            print("⏳ 审批仍在等待中，请稍后再查询")
        elif status_response.is_rejected:
            print(f"✗ 审批被拒绝: {status_response.remark}")
        elif status_response.is_expired:
            print("⏰ 审批已过期")

    except Exception as e:
        print(f"✗ 查询失败: {e}")


if __name__ == "__main__":
    print("AgentGuard SDK 审批功能示例\n")

    # 运行示例
    # 注意：需要替换 approval_id 为实际的审批 ID

    # 示例 1: 提交审批理由
    # submit_approval_reason_example()

    # 示例 2: 查询审批状态
    # query_approval_status_example()

    # 示例 3: 完整工作流
    # complete_approval_workflow_example()

    print("\n提示：请先替换代码中的 approval_id 为实际的审批 ID，然后取消注释相应的示例函数")
