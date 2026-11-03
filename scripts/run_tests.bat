@echo off
REM 运行所有单元测试 (Windows)

cd /d "%~dp0"

echo === 运行 autoaigc 单元测试 ===
echo.

python -m unittest discover -s tests -v

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ 所有测试通过
) else (
    echo.
    echo ✗ 测试失败，退出码: %ERRORLEVEL%
)

exit /b %ERRORLEVEL%
