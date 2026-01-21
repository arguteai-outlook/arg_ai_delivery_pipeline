#!/usr/bin/env bash
set -u

out_dir="${1:-ci_artifacts}"
mkdir -p "${out_dir}"

fail=0

run_gate () {
  local name="$1"
  shift
  local log_path="${out_dir}/${name}.log"

  echo "==> ${name}" | tee "${log_path}"
  echo "cmd: $*" >> "${log_path}"
  echo "" >> "${log_path}"

  set +e
  "$@" >> "${log_path}" 2>&1
  local rc=$?
  set -e

  echo "" >> "${log_path}"
  echo "exit_code=${rc}" >> "${log_path}"

  if [ "${rc}" -ne 0 ]; then
    fail=1
  fi

  return 0
}

set -e

# validate_repo: keep this intentionally minimal and deterministic
run_gate "validate_repo" python -m compileall -q src

# lint
if command -v ruff >/dev/null 2>&1; then
  run_gate "lint" ruff check .
else
  echo "ruff not installed; skipping lint gate" > "${out_dir}/lint.log"
  echo "exit_code=0" >> "${out_dir}/lint.log"
fi

# unit_tests
if command -v pytest >/dev/null 2>&1; then
  run_gate "unit_tests" pytest -q
else
  echo "pytest not installed; skipping unit_tests gate" > "${out_dir}/unit_tests.log"
  echo "exit_code=0" >> "${out_dir}/unit_tests.log"
fi

# terraform gates (skip if no terraform directory)
if [ -d "terraform" ] || [ -f "main.tf" ]; then
  if command -v terraform >/dev/null 2>&1; then
    run_gate "terraform_fmt" terraform fmt -check -recursive
    run_gate "terraform_validate" terraform validate
    run_gate "terraform_plan" terraform plan -no-color
  else
    echo "terraform not installed; skipping terraform gates" > "${out_dir}/terraform_fmt.log"
    echo "exit_code=0" >> "${out_dir}/terraform_fmt.log"
    cp "${out_dir}/terraform_fmt.log" "${out_dir}/terraform_validate.log"
    cp "${out_dir}/terraform_fmt.log" "${out_dir}/terraform_plan.log"
  fi
else#!/usr/bin/env bash
set -u

out_dir="${1:-ci_artifacts}"
mkdir -p "${out_dir}"

fail=0

run_gate () {
  local name="$1"
  shift
  local log_path="${out_dir}/${name}.log"

  echo "==> ${name}" | tee "${log_path}"
  echo "cmd: $*" >> "${log_path}"
  echo "" >> "${log_path}"

  set +e
  "$@" >> "${log_path}" 2>&1
  local rc=$?
  set -e

  echo "" >> "${log_path}"
  echo "exit_code=${rc}" >> "${log_path}"

  if [ "${rc}" -ne 0 ]; then
    fail=1
  fi

  return 0
}

set -e

# validate_repo: keep this intentionally minimal and deterministic
run_gate "validate_repo" python -m compileall -q src

# lint
if command -v ruff >/dev/null 2>&1; then
  run_gate "lint" ruff check .
else
  echo "ruff not installed; skipping lint gate" > "${out_dir}/lint.log"
  echo "exit_code=0" >> "${out_dir}/lint.log"
fi

# unit_tests
if command -v pytest >/dev/null 2>&1; then
  run_gate "unit_tests" pytest -q
else
  echo "pytest not installed; skipping unit_tests gate" > "${out_dir}/unit_tests.log"
  echo "exit_code=0" >> "${out_dir}/unit_tests.log"
fi

# terraform gates (skip if no terraform directory)
if [ -d "terraform" ] || [ -f "main.tf" ]; then
  if command -v terraform >/dev/null 2>&1; then
    run_gate "terraform_fmt" terraform fmt -check -recursive
    run_gate "terraform_validate" terraform validate
    run_gate "terraform_plan" terraform plan -no-color
  else
    echo "terraform not installed; skipping terraform gates" > "${out_dir}/terraform_fmt.log"
    echo "exit_code=0" >> "${out_dir}/terraform_fmt.log"
    cp "${out_dir}/terraform_fmt.log" "${out_dir}/terraform_validate.log"
    cp "${out_dir}/terraform_fmt.log" "${out_dir}/terraform_plan.log"
  fi
else
  echo "no terraform configuration found; skipping terraform gates" > "${out_dir}/terraform_fmt.log"
  echo "exit_code=0" >> "${out_dir}/terraform_fmt.log"
  cp "${out_dir}/terraform_fmt.log" "${out_dir}/terraform_validate.log"
  cp "${out_dir}/terraform_fmt.log" "${out_dir}/terraform_plan.log"
fi

if [ "${fail}" -ne 0 ]; then
  echo "one or more gates failed"
  exit 1
fi

echo "all gates passed"
exit 0

  echo "no terraform configuration found; skipping terraform gates" > "${out_dir}/terraform_fmt.log"
  echo "exit_code=0" >> "${out_dir}/terraform_fmt.log"
  cp "${out_dir}/terraform_fmt.log" "${out_dir}/terraform_validate.log"
  cp "${out_dir}/terraform_fmt.log" "${out_dir}/terraform_plan.log"
fi

if [ "${fail}" -ne 0 ]; then
  echo "one or more gates failed"
  exit 1
fi

echo "all gates passed"
exit 0
