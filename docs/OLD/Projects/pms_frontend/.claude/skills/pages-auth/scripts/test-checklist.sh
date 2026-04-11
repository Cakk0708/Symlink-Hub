#!/bin/bash

# PMS 多平台认证架构测试检查清单
# 使用方法：bash test-checklist.sh

echo "========================================="
echo "PMS 多平台认证架构测试检查清单"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查项目
check_item() {
    local description="$1"
    local command="$2"

    echo -n "☐ $description ... "
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}"
        return 0
    else
        echo -e "${RED}✗ 失败${NC}"
        return 1
    fi
}

echo "=== 文件结构检查 ==="
check_item "authProviders.js 配置文件" "test -f common/config/authProviders.js"
check_item "LoginProvider 基类" "test -f common/auth/core/LoginProvider.js"
check_item "ProviderRegistry 注册中心" "test -f common/auth/core/ProviderRegistry.js"
check_item "EnvironmentDetector 环境检测" "test -f common/auth/core/EnvironmentDetector.js"
check_item "FeishuProvider 飞书实现" "test -f common/auth/providers/FeishuProvider.js"
check_item "CallbackHandler 回调处理" "test -f common/auth/callback/CallbackHandler.js"
check_item "utils 工具函数" "test -f common/auth/utils.js"
check_item "auth/index 统一导出" "test -f common/auth/index.js"
check_item "login-select.vue 登录选择页" "test -f pages/auth/login-select.vue"
check_item "callback.vue 回调处理页" "test -f pages/auth/callback.vue"

echo ""
echo "=== 关键代码检查 ==="
check_item "hasValidToken 使用 Boolean()" "grep -q 'return Boolean(token && token.access_token)' common/auth.js"
check_item "global.js 中 showLoginSelectionPage" "grep -q 'function showLoginSelectionPage' common/global.js"
check_item "pages.json 中 login-select 路由" "grep -q 'pages/auth/login-select' pages.json"
check_item "pages.json 中 callback 路由" "grep -q 'pages/auth/callback' pages.json"

echo ""
echo "=== 飞书容器环境测试 ==="
echo "请在飞书 App 内打开 H5 并确认："
echo "  ☐ checkFeishuContainer() 返回 true"
echo "  ☐ tt.requestAuthCode 正常调用"
echo "  ☐ JWT token 正常获取和保存"
echo "  ☐ 无无限登录循环"
echo "  ☐ 页面正常加载"
echo ""

echo "=== 浏览器环境测试 ==="
echo "请在浏览器中直接访问系统并确认："
echo "  ☐ 显示登录选择页面"
echo "  ☐ 选择飞书后正确跳转授权页面"
echo "  ☐ URL 参数正确（client_id、redirect_uri、state）"
echo "  ☐ 授权后回调正确接收 code"
echo "  ☐ state 校验通过"
echo "  ☐ /auth/login 接口调用成功"
echo "  ☐ token 保存成功"
echo "  ☐ 页面跳转回原访问页面"
echo ""

echo "=== 异常场景测试 ==="
echo "  ☐ 用户拒绝授权处理正确"
echo "  ☐ state 校验失败提示正确"
echo "  ☐ code 过期处理正确"
echo "  ☐ 网络请求失败提示正确"
echo ""

echo "========================================="
echo "测试检查完成"
echo "========================================="
