#!/usr/bin/env python3
"""
MCP Service Test Simulator
模拟AI模型调用MCP服务进行各种MATLAB操作的测试脚本
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("mcp_test.log")
    ]
)
logger = logging.getLogger("MCP_Test_Simulator")

class MCPTestSimulator:
    """模拟MCP客户端调用"""
    
    def __init__(self):
        self.test_results = []
        
    async def run_test_case(self, test_name: str, test_func, *args, **kwargs):
        """运行单个测试用例"""
        logger.info(f"🧪 开始测试: {test_name}")
        start_time = time.time()
        
        try:
            result = await test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            self.test_results.append({
                "test_name": test_name,
                "status": "PASS",
                "duration": f"{duration:.2f}s",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"✅ 测试通过: {test_name} (耗时: {duration:.2f}s)")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            self.test_results.append({
                "test_name": test_name,
                "status": "FAIL",
                "duration": f"{duration:.2f}s",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.error(f"❌ 测试失败: {test_name} - {str(e)}")
            return None
    
    async def test_basic_matlab_operations(self):
        """测试基本MATLAB操作"""
        from main import runMatlabCode, getVariable
        
        # 测试1: 简单数学运算
        await self.run_test_case(
            "基本数学运算",
            runMatlabCode,
            "a = 2 + 3; b = a * 4; c = sqrt(b);"
        )
        
        # 测试2: 获取变量值
        result = await self.run_test_case(
            "获取变量值",
            getVariable,
            "a"
        )
        
        # 测试3: 矩阵操作
        await self.run_test_case(
            "矩阵操作",
            runMatlabCode,
            "M = [1 2 3; 4 5 6; 7 8 9]; det_M = det(M); inv_M = inv(M);"
        )
        
        # 测试4: 字符串操作
        await self.run_test_case(
            "字符串操作",
            runMatlabCode,
            "str1 = 'Hello'; str2 = 'World'; combined = strcat(str1, ' ', str2);"
        )
        
        return True
    
    async def test_advanced_matlab_functions(self):
        """测试高级MATLAB功能"""
        from main import runMatlabCode, getVariable
        
        # 测试1: 绘图功能
        await self.run_test_case(
            "绘图功能",
            runMatlabCode,
            """
            x = 0:0.1:2*pi;
            y = sin(x);
            figure('Visible', 'off');
            plot_result = plot(x, y);
            title('Sine Wave Test');
            """
        )
        
        # 测试2: 文件操作
        await self.run_test_case(
            "文件操作测试",
            runMatlabCode,
            """
            test_data = rand(5, 3);
            save('test_data.mat', 'test_data');
            file_exists = exist('test_data.mat', 'file');
            """
        )
        
        # 测试3: 函数定义和调用
        await self.run_test_case(
            "函数定义测试",
            runMatlabCode,
            """
            test_function = @(x, y) x.^2 + y.^2;
            result = test_function(3, 4);
            """
        )
        
        return True
    
    async def test_error_handling(self):
        """测试错误处理"""
        from main import runMatlabCode
        
        # 测试1: 语法错误
        await self.run_test_case(
            "语法错误处理",
            runMatlabCode,
            "invalid syntax here;"
        )
        
        # 测试2: 未定义变量
        await self.run_test_case(
            "未定义变量错误",
            runMatlabCode,
            "result = undefined_variable * 2;"
        )
        
        # 测试3: 矩阵维度错误
        await self.run_test_case(
            "矩阵维度错误",
            runMatlabCode,
            "A = [1 2; 3 4]; B = [1; 2; 3]; C = A + B;"
        )
        
        return True
    
    async def test_input_handling(self):
        """测试输入处理功能"""
        from main import handleMatlabInput
        
        # 测试模拟输入处理
        test_prompts = [
            "请输入文件名:",
            "是否继续处理数据? (y/n):",
            "请输入采样频率:",
            "选择处理模式 (1-3):"
        ]
        
        for prompt in test_prompts:
            await self.run_test_case(
                f"输入处理: {prompt}",
                handleMatlabInput,
                prompt
            )
        
        return True
    
    async def test_arduino_system_integration(self):
        """测试Arduino系统集成"""
        from main import runMatlabCode
        
        # 检查Arduino相关文件是否存在
        await self.run_test_case(
            "检查Arduino系统文件",
            runMatlabCode,
            """
            arduino_files = {
                'run_arduino_system.m', 
                'auto_input.m',
                'test_arduino_input.m'
            };
            files_exist = arrayfun(@(f) exist(f{1}, 'file'), arduino_files);
            all_files_exist = all(files_exist);
            """
        )
        
        # 测试auto_input函数（如果存在）
        await self.run_test_case(
            "测试auto_input函数",
            runMatlabCode,
            """
            if exist('auto_input.m', 'file')
                % 模拟调用auto_input
                fprintf('auto_input.m file found and can be called\\n');
                auto_input_available = true;
            else
                fprintf('auto_input.m file not found\\n');
                auto_input_available = false;
            end
            """
        )
        
        return True
    
    def print_summary(self):
        """打印测试总结"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*60)
        print("🔍 MCP 服务测试总结")
        print("="*60)
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests} ✅")
        print(f"失败测试: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        print("="*60)
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test_name']}: {result.get('error', 'Unknown error')}")
        
        print(f"\n📝 详细日志已保存到: mcp_test.log")
        
        # 保存测试结果到JSON文件
        with open("mcp_test_results.json", "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"📊 测试结果已保存到: mcp_test_results.json")

async def main():
    """主测试函数"""
    print("🚀 启动 MCP 服务测试模拟器")
    print("="*60)
    
    # 首先检查MATLAB连接
    try:
        from main import eng
        logger.info("✅ MATLAB 引擎连接成功")
    except Exception as e:
        logger.error(f"❌ MATLAB 引擎连接失败: {e}")
        logger.error("请确保:")
        logger.error("1. MATLAB 已启动")
        logger.error("2. 已运行 matlab.engine.shareEngine")
        logger.error("3. 或使用批处理脚本自动启动")
        return
    
    simulator = MCPTestSimulator()
    
    # 运行所有测试
    test_suites = [
        ("基本MATLAB操作", simulator.test_basic_matlab_operations),
        ("高级MATLAB功能", simulator.test_advanced_matlab_functions),
        ("错误处理", simulator.test_error_handling),
        ("输入处理", simulator.test_input_handling),
        ("Arduino系统集成", simulator.test_arduino_system_integration),
    ]
    
    for suite_name, suite_func in test_suites:
        logger.info(f"🔄 开始测试套件: {suite_name}")
        await suite_func()
        logger.info(f"✅ 完成测试套件: {suite_name}")
        print("-" * 40)
    
    # 打印测试总结
    simulator.print_summary()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
    except Exception as e:
        logger.error(f"💥 测试过程中出现意外错误: {e}")
        sys.exit(1) 