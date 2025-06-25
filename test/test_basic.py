##########test_basic.py: 基础功能测试脚本 ##################
# 变更记录: [2025-06-25] @李祥光 [创建基础功能测试]########
# 输入: [无] | 输出: [测试结果报告]###############


###########################文件下的所有函数###########################
"""
test_config_loading：测试配置加载功能
test_logger_setup：测试日志系统设置
test_video_file_detection：测试视频文件检测功能
test_directory_creation：测试目录创建功能
run_all_tests：运行所有测试用例
"""
###########################文件下的所有函数###########################

#########mermaid格式说明所有函数的调用关系说明开始#########
"""
flowchart TD
    A[测试启动] --> B[run_all_tests]
    B --> C[test_config_loading]
    B --> D[test_logger_setup]
    B --> E[test_video_file_detection]
    B --> F[test_directory_creation]
    C --> G[配置测试结果]
    D --> H[日志测试结果]
    E --> I[文件检测测试结果]
    F --> J[目录创建测试结果]
    G --> K[汇总测试报告]
    H --> K
    I --> K
    J --> K
"""
#########mermaid格式说明所有函数的调用关系说明结束#########

import os
import sys
import tempfile
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.config import get_default_config, get_supported_formats, get_preset_config
    from utils.logger import setup_logger, log_info, log_error
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在项目根目录下运行此测试脚本")
    sys.exit(1)


def test_config_loading():
    """
    test_config_loading 功能说明:
    # 测试配置文件加载功能
    # 输入: [无] | 输出: [bool 测试是否通过]
    """
    try:
        print("\n🧪 测试配置加载功能...")
        
        # 测试默认配置
        default_config = get_default_config()
        assert isinstance(default_config, dict), "默认配置应该是字典类型"
        assert 'threshold' in default_config, "配置中应包含threshold参数"
        
        # 测试支持格式
        formats = get_supported_formats()
        assert isinstance(formats, dict), "支持格式应该是字典类型"
        assert 'input_formats' in formats, "应包含输入格式列表"
        
        # 测试预设配置
        balanced_config = get_preset_config('balanced')
        assert isinstance(balanced_config, dict), "预设配置应该是字典类型"
        
        print("✅ 配置加载测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置加载测试失败: {e}")
        return False


def test_logger_setup():
    """
    test_logger_setup 功能说明:
    # 测试日志系统设置功能
    # 输入: [无] | 输出: [bool 测试是否通过]
    """
    try:
        print("\n🧪 测试日志系统设置...")
        
        # 创建临时日志目录
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = os.path.join(temp_dir, "test_logs")
            
            # 设置日志器
            logger = setup_logger(log_dir, "INFO")
            assert logger is not None, "日志器不应为空"
            
            # 测试日志记录
            log_info("这是一条测试信息")
            log_error("这是一条测试错误")
            
            # 检查日志文件是否创建
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
            assert len(log_files) > 0, "应该创建日志文件"
            
            ###########################修改开始 2025-6-25 李祥光  #######################
            # 关闭日志处理器以释放文件锁
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
            ###########################修改结束 2025-6-25 李祥光  #######################
        
        print("✅ 日志系统测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 日志系统测试失败: {e}")
        return False


def test_video_file_detection():
    """
    test_video_file_detection 功能说明:
    # 测试视频文件检测功能
    # 输入: [无] | 输出: [bool 测试是否通过]
    """
    try:
        print("\n🧪 测试视频文件检测功能...")
        
        # 测试支持的视频格式
        formats = get_supported_formats()
        input_formats = formats['input_formats']
        
        # 测试格式检测
        test_files = [
            "test.mp4",
            "test.avi", 
            "test.mov",
            "test.txt",  # 非视频文件
            "test.jpg"   # 非视频文件
        ]
        
        for filename in test_files:
            is_video = any(filename.lower().endswith(ext) for ext in input_formats)
            expected = filename.endswith(('.mp4', '.avi', '.mov'))
            assert is_video == expected, f"文件 {filename} 的检测结果不正确"
        
        print("✅ 视频文件检测测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 视频文件检测测试失败: {e}")
        return False


def test_directory_creation():
    """
    test_directory_creation 功能说明:
    # 测试目录创建功能
    # 输入: [无] | 输出: [bool 测试是否通过]
    """
    try:
        print("\n🧪 测试目录创建功能...")
        
        # 在临时目录中测试
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dirs = ['output', 'logs', 'temp', 'config']
            
            for dir_name in test_dirs:
                dir_path = os.path.join(temp_dir, dir_name)
                os.makedirs(dir_path, exist_ok=True)
                assert os.path.exists(dir_path), f"目录 {dir_name} 创建失败"
                assert os.path.isdir(dir_path), f"{dir_name} 不是有效目录"
        
        print("✅ 目录创建测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 目录创建测试失败: {e}")
        return False


def run_all_tests():
    """
    run_all_tests 功能说明:
    # 运行所有测试用例并生成报告
    # 输入: [无] | 输出: [无，打印测试报告]
    """
    print("🚀 开始运行基础功能测试")
    print("=" * 50)
    
    tests = [
        ("配置加载", test_config_loading),
        ("日志系统", test_logger_setup),
        ("视频文件检测", test_video_file_detection),
        ("目录创建", test_directory_creation)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试 {test_name} 发生异常: {e}")
            failed += 1
    
    # 生成测试报告
    print("\n" + "=" * 50)
    print("📊 测试报告")
    print(f"总测试数: {len(tests)}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"成功率: {(passed/len(tests)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查相关功能")
    
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()