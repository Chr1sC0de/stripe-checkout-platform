#! /bin/bash

# shellcheck disable=SC2155
export source_folder=$(dirname -- "${BASH_SOURCE[0]}")

cd "$source_folder" || exit

# shellcheck disable=SC2046,SC2001,SC2005
github_open_id_connect_providers=$(echo $(aws iam list-open-id-connect-providers) | grep github | sed "s/.\+\s\(arn:.\+githubusercontent.\+\)/\1/")

if [[ -z $github_open_id_connect_providers ]]; then
    echo "INFO: No Github Open ID connect provider found creating..."
    aws iam create-open-id-connect-provider \
        --url https://token.actions.githubusercontent.com \
        --client-id-list sts.amazonaws.com
    # shellcheck disable=SC2046,SC2001,SC2005
    github_open_id_connect_providers=$(echo $(aws iam list-open-id-connect-providers) | grep github | sed "s/.\+\s\(arn:.\+githubusercontent.\+\)/\1/")
    echo "INFO: Finished creating Github Open ID Connect Provider"
fi

echo "INFO: Open ID Connect Provider: $github_open_id_connect_providers"

trust_policy_file="role-trust-policy.json"
permissions_policy_file="role-permissions-policy.json"

if [[ -f $trust_policy_file ]]; then
    rm $trust_policy_file
fi

if [[ -f $permissions_policy_file ]]; then
    rm $permissions_policy_file
fi

organization_and_repository=$(git remote -v | grep ".\+ (fetch)" | sed "s/.\+:\(.\+\).git.\+/\1/")

echo "INFO: Open ID Connect Provider: $organization_and_repository"

echo "{
    \"Version\": \"2012-10-17\",
    \"Statement\": [
        {
            \"Effect\": \"Allow\",
            \"Principal\": {
                \"Federated\": \"${github_open_id_connect_providers}\"
            },
            \"Action\": \"sts:AssumeRoleWithWebIdentity\",
            \"Condition\": {
                \"StringEquals\": {
                    \"token.actions.githubusercontent.com:aud\": \"sts.amazonaws.com\"
                },
                \"StringLike\": {
                    \"token.actions.githubusercontent.com:sub\": \"repo:${organization_and_repository}:*\"
                }
            }
        }
    ]
}
" >$trust_policy_file

stack_qualifier=$(aws cloudformation describe-stacks --stack-name CDKToolkit | grep ExportName: | sed "s/.\+-\(.\+\)-.\+/\1/")

echo "{
    \"Version\": \"2012-10-17\",
    \"Statement\": [
        {
            \"Sid\": \"assumerole\",
            \"Effect\": \"Allow\",
            \"Action\": [
                \"sts:AssumeRole\",
                \"iam:PassRole\"
            ],
            \"Resource\": [
                \"arn:aws:iam::*:role/cdk-readOnlyRole\",
                \"arn:aws:iam::*:role/cdk-$stack_qualifier*\"
            ]
        }
    ]
}
" >$permissions_policy_file

role_name=AWSGitHubActionsRole

aws iam create-role \
    --role-name $role_name \
    --assume-role-policy-document "file://$trust_policy_file" >create-role.log

# attach the system administrator policy

aws iam attach-role-policy \
    --role-name $role_name \
    --policy-arn arn:aws:iam::aws:policy/job-function/SystemAdministrator

# attach the

aws iam put-role-policy \
    --role-name $role_name \
    --policy-name CKDPolicy \
    --policy-document "file://$permissions_policy_file"
