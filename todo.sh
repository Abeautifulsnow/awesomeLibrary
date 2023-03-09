#!/bin/zsh

files=($(git diff --cached --name-only --diff-filter=AM))

for file in "${files[@]}"; do
	if [[ -n "$file" && "$file" == *py ]]; then
		# 搜索文件关键词及行数
		if grep -Hin TODO "$file"; then
			echo "Blocking commit as TODO was found."
			exit 1
		fi
	fi
done
