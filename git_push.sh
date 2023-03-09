#!/bin/bash

PrintRED="\033[31m%s\033[0m\n" 2>/dev/null
PrintGreen="\033[32m%s\033[0m\n" 2>/dev/null
PrintYellow="\033[33m%s\033[0m\n" 2>/dev/null

function create_branch_if_not_exist() {
	default_branch=$1

	branch_arr=$(git branch -a)
	# shellcheck disable=SC2066
	for branch in "${branch_arr}"; do
		branch_in=$(echo "${branch}" | grep "${default_branch}")
		if [[ ${branch_in} != "" ]]; then
			default_branch=${default_branch}
			git checkout "${default_branch}"
		else
			printf $PrintRED "💫💫💫 Branch ==> ${default_branch} does not exist, we will create it..."
			git checkout -b "${default_branch}"
		fi
		printf $PrintGreen "✨✨✨ Current branch is: ${default_branch}"
	done
}

function gen_commit_if_empty() {
	commit=$1

	git_comment="$(date +%F' '%r)"
	if [[ ${commit} == "" ]]; then
		commit="${git_comment} push code"
	else
		commit=${commit}
	fi
	printf $PrintGreen "✨✨✨ The commit's content are: ${commit}"
}

function push_code() {
	while true; do
		read -r -p "🌝🌝🌝 Continue or not? [Y/n] " input

		case $input in
		[yY][eE][sS] | [yY])
			printf $PrintYellow "Continue to submit..."
			git add -A
			git commit -m "${commit}" || exit 1
			git push origin ${default_branch}
			exit 1
			;;

		[nN][oO] | [nN])
			printf $PrintRED "💥💥💥 Submit interrupted..."
			exit 1
			;;
		*)
			printf $PrintRED "💥💥💥 Input error, please retry it..."
			;;
		esac
	done
}

# Execute the flow of pushing code to git repository.
function exe_flow() {
	commit_arg=$1
	branch_arg=$2
	create_branch_if_not_exist "${branch_arg}"
	git status
	gen_commit_if_empty "${commit_arg}"
	push_code
}

function git_echo() {
	command printf %s\\n "$*" 2>/dev/null
}

function Error_print() {
	printf $PrintRED "Error:"
	printf $PrintYellow "Current input: $*"
	printf $PrintYellow "See usage info by: bash git_push.sh --help"
}

function get_help() {
	local commit_in
	local branch_in

	if [[ $# -lt 0 ]]; then
		Error_print
		return
	elif [[ $# == 0 ]]; then
		echo
	elif [[ $# -ge 1 && $# -lt 5 ]]; then
		local mFirst=0
		local bFirst=0
		for i in "$@"; do
			case $i in
			'-h' | 'help' | '--help')
				git_echo "bash git_push.sh [Options]"
				git_echo
				git_echo "Usage:"
				git_echo "	bash git_push.sh --help		Show this message."
				git_echo
				git_echo "Options:"
				git_echo "	-m, --commit			default: $(date +%F' '%r)	Commit comment of writing it into 'git commit -m ...'"
				git_echo "	-b, --branch			default: 'main'			The which 「git branch」 you want to push."
				exit 0
				;;
			'-m' | '--commit')
				mFirst=1
				shift
				if [ $bFirst == 1 ]; then
					commit_in=$2
				else
					commit_in=$1
				fi
				;;
			'-b' | '--branch')
				bFirst=1
				shift
				if [ $mFirst == 1 ]; then
					branch_in=$2
				else
					branch_in=$1
				fi
				;;
			*) ;;
			esac
		done
	else
		Error_print $@
		return
	fi

	git_echo "branch: ${branch_in:-main}"
	git_echo "commit: ${commit_in:-$(date +%F' '%r)}"
	exe_flow "${commit_in}" "${branch_in}"
	printf $PrintGreen "💫💫💫 All done..."
	exit 0
}

get_help $@
