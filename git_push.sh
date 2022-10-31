#!/bin/bash
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
            echo -e "\033[31m💫💫💫 Branch ==> ${default_branch} does not exist, we will create it...\033[0m"
            git checkout -b "${default_branch}"
        fi
        echo -e "\033[32m✨✨✨ Current branch is: ${default_branch}\033[0m"
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
    echo -e "\033[32m✨✨✨ The commit's content are: ${commit}\033[0m"
}

function push_code() {
    while true; do
        read -r -p "🌝🌝🌝 Continue or not? [Y/n] " input

        case $input in
        [yY][eE][sS] | [yY])
            echo -e "\033[33mContinue to submit...\033[0m"
            git add -A
            git commit -m "${commit}"
            git push origin ${default_branch}
            exit 1
            ;;

        [nN][oO] | [nN])
            echo -e "\033[31m💥💥💥 Submit interrupted...\033[0m"
            exit 1
            ;;
        *)
            echo -e "\033[31m💥💥💥 Input error, please retry it...\033[0m"
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

commit_in=$1
branch_in=${2:-master}
exe_flow "${commit_in}" "${branch_in}"
echo -e "\033[32m💫💫💫 All done...\033[0m"
exit 0