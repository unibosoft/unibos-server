#!/usr/bin/env bash
# Test CLI Simplification - Verify all commands work as expected

set -e

echo "=========================================="
echo "Testing CLI Simplification"
echo "=========================================="
echo

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

test_count=0
pass_count=0
fail_count=0

run_test() {
    local test_name="$1"
    local command="$2"

    test_count=$((test_count + 1))
    echo -e "${BLUE}Test $test_count: $test_name${NC}"
    echo "Command: $command"

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}✗ FAIL${NC}"
        fail_count=$((fail_count + 1))
    fi
    echo
}

echo "=========================================="
echo "1. Testing unibos-dev Direct Commands"
echo "=========================================="
echo

# Test that commands exist at top level
run_test "unibos-dev status" "unibos-dev status --help"
run_test "unibos-dev run" "unibos-dev run --help"
run_test "unibos-dev shell" "unibos-dev shell --help"
run_test "unibos-dev test" "unibos-dev test --help"
run_test "unibos-dev migrate" "unibos-dev migrate --help"
run_test "unibos-dev makemigrations" "unibos-dev makemigrations --help"
run_test "unibos-dev logs" "unibos-dev logs --help"
run_test "unibos-dev stop" "unibos-dev stop --help"

echo "=========================================="
echo "2. Testing Backwards Compatibility"
echo "=========================================="
echo

# Test that old paths still work
run_test "unibos-dev dev run" "unibos-dev dev run --help"
run_test "unibos-dev dev shell" "unibos-dev dev shell --help"
run_test "unibos-dev dev test" "unibos-dev dev test --help"
run_test "unibos-dev dev migrate" "unibos-dev dev migrate --help"
run_test "unibos-dev dev makemigrations" "unibos-dev dev makemigrations --help"
run_test "unibos-dev dev logs" "unibos-dev dev logs --help"
run_test "unibos-dev dev stop" "unibos-dev dev stop --help"

echo "=========================================="
echo "3. Testing unibos-manager Standalone"
echo "=========================================="
echo

# Test that unibos-manager exists and works
run_test "unibos-manager exists" "which unibos-manager"
run_test "unibos-manager help" "unibos-manager --help"
run_test "unibos-manager status" "unibos-manager status --help"
run_test "unibos-manager deploy" "unibos-manager deploy --help"
run_test "unibos-manager ssh" "unibos-manager ssh --help"
run_test "unibos-manager tui" "unibos-manager tui --help"

echo "=========================================="
echo "4. Testing Other Command Groups"
echo "=========================================="
echo

# Test that other command groups still work
run_test "unibos-dev deploy" "unibos-dev deploy --help"
run_test "unibos-dev db" "unibos-dev db --help"
run_test "unibos-dev git" "unibos-dev git --help"
run_test "unibos-dev platform" "unibos-dev platform --help"

echo "=========================================="
echo "5. Testing Manager via Dev CLI"
echo "=========================================="
echo

# Test that manager is still accessible via unibos-dev
run_test "unibos-dev manager" "unibos-dev manager --help"
run_test "unibos-dev manager status" "unibos-dev manager status --help"

echo "=========================================="
echo "Summary"
echo "=========================================="
echo -e "Total Tests: $test_count"
echo -e "${GREEN}Passed: $pass_count${NC}"
echo -e "${RED}Failed: $fail_count${NC}"
echo

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
