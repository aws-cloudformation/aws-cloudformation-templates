# cfnresponse

The `cfnresponse` package provides a Python module for working with AWS CloudFormation custom resources in AWS Lambda environments. This package allows you to create, update, and delete CloudFormation custom resources using Lambda functions.

## Usage

The `cfnresponse` package is designed to be used within AWS Lambda functions that serve as custom resource handlers for CloudFormation stacks. Custom resources allow you to extend CloudFormation's capabilities by executing custom logic during stack creation, update, or deletion.

For examples of how to use the `cfnresponse` package, refer to the `samples` folder in this repository. Each sample demonstrates different scenarios of CloudFormation custom resource handling.

## Project Structure

The project repository is organized as follows:

- `cfnresponse`: Contains the `__init__.py` file that provides the `cfnresponse` module.
- `LICENSE`: The license information for the package.
- `README.md`: This README file with usage instructions.
- `samples`: Contains sample Lambda functions demonstrating `cfnresponse` usage (actual code not provided in this README).
- `setup.py`: Package setup configuration.
- `tests`: Contains test cases for the `cfnresponse` package.