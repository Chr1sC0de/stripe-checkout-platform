PARAMETER_NAME="/$COMPANY/$DEVELOPMENT_ENVIRONMENT/$1"

echo "INFO: PARAMETER_NAME=$PARAMETER_NAME"
echo "INFO: Started running lambda $1"

LAMBDA_ARN=$(\
    aws ssm get-parameter --name "$PARAMETER_NAME" | \
    grep Value: | \
    sed "s/.\+Value: \(arn.\+\)/\1/")

aws lambda invoke \
    --function-name "$LAMBDA_ARN" \
    --cli-binary-format base64 \
    --payload '{}' \
    response.json

echo "INFO: Finished running lambda $1"