#!/bin/bash
# 运行所有单元测试

cd "$(dirname "$0")"

echo "=== 运行 autoaigc 单元测试 ==="
echo ""

python -m unittest discover -s tests -v

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✓ 所有测试通过"
else
    echo "✗ 测试失败，退出码: $exit_code"
fi

exit $exit_code
