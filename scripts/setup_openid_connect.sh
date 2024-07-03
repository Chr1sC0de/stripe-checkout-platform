#! /bin/bash

# shellcheck disable=SC2155
export source_folder=$(dirname -- "${BASH_SOURCE[0]}")

cd "$source_folder" || exit

    # shellcheck disable=SC2046,SC2001,SC2005
github_open_id_connect_providers=$(echo $(aws iam list-open-id-connect-providers) | sed "s/.\+\s\(arn:.\+githubusercontent.\+\)/\1/")

if [[ -z $github_open_id_connect_providers ]]; then
    echo "INFO: No Github Open ID connect provider found creating..."
    aws iam create-open-id-connect-provider \
        --url https://token.actions.githubusercontent.com \
        --client-id-list sts.amazonaws.com
    # shellcheck disable=SC2046,SC2001,SC2005
    github_open_id_connect_providers=$(echo $(aws iam list-open-id-connect-providers) | sed "s/.\+\s\(arn:.\+githubusercontent.\+\)/\1/")
    echo "INFO: Finished creating Github Open ID Connect Provider"
fi;

rm role-trust-policy.json

organization_and_repository=$(git remote -v | grep ".\+ (fetch)" | sed "s/.\+:\(.\+\).git.\+/\1/")

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
">role-trust-policy.json

aws iam create-role \
    --role-name Test-Role \
    --assume-role-policy-document file://role-trust-policy.json > create-role.log;

aws iam attach-role-policy \
    --role-name Test-Role \
    --policy-arn arn:aws:iam::aws:policy/AmazonCognitoPowerUser;
