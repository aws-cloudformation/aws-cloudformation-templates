## DataPipeline with multiple StringValue's
The CloudFormation documentation shows how to provide a StringValue for atomic values as part of your DataPipeline definition. 
The documentation also lacks a little in providing an example of how to cross reference RefValue as part of one pipeline object
with properties of another. 

### Usage
This template is for use as-is and does not require any Parameters or user input whatsoever. You can deploy this in any region
that supports DataPipeline and CloudFormation. The Pipeline itself does not serve any particular purpose, rather, this exemplifies the translation of DataPipeline definitions using Cloudformation. 

You can see when we look at the following: 

```
              {
                "Key": "applications",
                "StringValue": "spark"
              },
              {
                "Key": "applications",
                "StringValue": "hive"
              },
              {
                "Key": "applications",
                "StringValue": "pig"
              },
```

We can pass multiple 'StringValue' the same 'Key' multiple times

And here we have an example of providing parameters for RefValues given in a different part of the PipelineObjects: 

``` 
         {
            "Id": "coresite",
            "Name": "coresite",
            "Fields": [
              {
                "Key": "type",
                "StringValue": "EmrConfiguration"
              },
              {
                "Key": "classification",
                "StringValue": "core-site"
              },
              {
                "Key": "property",
                "RefValue": "io-file-buffer-size"
              },
              {
                "Key": "property",
                "RefValue": "fs-s3-block-size"
              }
            ]
          },
          {
            "Id": "io-file-buffer-size",
            "Name": "io-file-buffer-size",
            "Fields": [
              {
                "Key": "type",
                "StringValue": "Property"
              },
              {
                "Key" : "value",
                "StringValue": "4096"
              },
              {
                "Key" : "key",
                "StringValue": "io.file.buffer.size"
              }

            ]
          },
```

### Basis
The template was originally requested as a 1:2:1 copy of the DataPipeline definition found in the Documentation here: 
http://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/dp-object-emrconfiguration.html
