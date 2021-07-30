# OPG Infra Costing Action

Contains a Python application to fetch data from the AWS Cost Explorer API for each AWS service for the account specified between the two the dates. This data is the converted and pused to a specificed metrics collection end point (such as OPG Metrics).

This application is the wrapped in a docker container (see the Dockerfile) so it can be utilised as a Github Action (see action.yml).

## Notes & Assumptions

The python application presumes it is running as a pre-authorised session which can assume the role based (via `--arn` argument) - you will likely need to use [another action](https://github.com/aws-actions/configure-aws-credentials) to configure the environment for your workflow step.

Data is sent in chunks of 20 at a time, this is based on the limitation of the recieving tooling and may change later.
