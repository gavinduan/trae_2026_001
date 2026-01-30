#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main script for Chinese New Year Customs QA System
Demonstrates the RAG workflow for answering questions about Chinese New Year customs.
"""

from rag_controller import RAGController

def main():
    """
    Main function to run the Chinese New Year Customs QA System.
    """
    print("===========================================")
    print("中国新年习俗问答系统")
    print("===========================================")
    print("你可以问我关于中国新年习俗的问题，例如：")
    print("- 为啥要倒贴福？")
    print("- 守岁是干啥的？")
    print("- 压岁钱是怎么来的？")
    print("- 那福字什么时候贴？")
    print("输入 '退出' 或 'exit' 结束对话")
    print("===========================================")

    # Initialize RAG controller
    knowledge_base_path = "../openspec/knowledge-base.json"
    rag_controller = RAGController(knowledge_base_path)

    while True:
        # Get user input
        question = input("\n你问：").strip()

        # Check if user wants to exit
        if question in ['退出', 'exit']:
            print("再见！")
            break

        # Check if question is empty
        if not question:
            print("请输入问题。")
            continue

        try:
            # Process query through RAG workflow
            answer = rag_controller.process_query(question)

            # Print the answer
            print(f"我答：{answer}")
        except Exception as e:
            print(f"处理问题时出错：{e}")
            print("请尝试重新输入问题。")

if __name__ == "__main__":
    main()
