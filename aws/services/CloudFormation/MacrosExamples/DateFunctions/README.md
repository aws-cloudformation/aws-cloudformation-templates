# Date functions

Provides string transformation utility functions.

## Basic Usage

Place the transform where you would like the output to be placed and provide the input string as the value for the
InputString Parameter. The example below shows converting an input parameter to upper case and setting it as the value
for a tag on an s3 bucket.

```yaml
Parameters:
  Date:
    Default: "This is a date"
    Type: String
    AllowedPattern: "^$|^\\d{4}(-\\d\\d(-\\d\\d(T\\d\\d:\\d\\d(:\\d\\d)?(\\.\\d+)?(([+-]\\d\\d:\\d\\d)|Z)?)?)?)?$"
Resources:
  S3Bucket:
    Type: "AWS::S3::Bucket"
    Properties:
      Tags:
        - Key: Upper
          Value:
            'Fn::Transform':
             - Name: 'Date'
               Parameters:
                 Date: !Ref Date
                 Operation: Current
```
## Parameters



| Name | Description |
|------|-------------|
| Operation | Operation to perform  [Available Operations](#AvailableOperations)  |
| Date | Date to use (defaults to `now`) |
| Date2 | Date to use for `Days` operation (also defaults to `now`)
| Days | Number of days to add or subtract in the `Add` or `Subtract` operations |

## Available Operations

### Current

Returns a copy of the current date and time in ISO format
 
### Add

Adds the `Days` parameter value to the `Date` value.

### Subtract

Subtracts the `Days` from the `Date`

### Days

Calculates the number of days between `Date` and `Date2`

