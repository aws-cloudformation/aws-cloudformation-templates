# DatetimeNow functions

Provides current datetime as a formmated string.

## Basic Usage

Place the transform where you would like the output to be placed and provide the string format as the value for the
format Parameter. The macro uses Python so the supported format codes match those used by the python `strftime` method.
Full list of supported codes can be found [here](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes).

The example below shows return the current date time as a string in the formation 'YYYY-MM-DD hh:mm:ss' and setting it as the value
for a tag on an s3 bucket.

```yaml
Resources:
  S3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      Tags:
        - Key: DatetimeNow
          Value:
            'Fn::Transform':
             - Name: 'String'
               Parameters:
                 param: '%Y-%m-%d %H:%M:%S'
```

## Author

[Dan Johns](https://github.com/danjhd)
Senior SA Engineer
Amazon Web Services
