# Sample Data for Amazon Q Business

This directory contains sample company documents that can be used to test the Amazon Q Business Enterprise template.

## Document Structure

```
sample-data/
├── policies/           # Company policies (HR Department)
│   ├── employee-handbook.md
│   └── expense-policy.md
├── procedures/         # IT procedures (IT Department)
│   └── it-security-procedures.md
├── manuals/           # Technical manuals (Engineering Department)
│   └── engineering-onboarding.md
├── faqs/              # Customer support FAQs (Support Department)
│   └── customer-support-faq.md
└── README.md          # This file
```

## Document Metadata

Each document includes metadata that will be indexed by Q Business:

- **Document Type**: Policy, Procedure, Manual, FAQ, etc.
- **Department**: HR, IT, Engineering, Customer Support, etc.
- **Confidentiality**: Public, Internal, Confidential, Restricted
- **Last Modified**: Date of last update

## Sample Content

### Policies (HR Department)
- **Employee Handbook**: Company policies, benefits, code of conduct
- **Expense Policy**: Travel expenses, reimbursement procedures, approval workflows

### Procedures (IT Department)
- **IT Security Procedures**: Password management, access control, incident response

### Manuals (Engineering Department)
- **Engineering Onboarding**: New developer setup, tools, processes, team structure

### FAQs (Customer Support)
- **Customer Support FAQ**: Common questions, troubleshooting, contact information

## Using the Sample Data

### Automated Setup
Use the provided script to automatically create an S3 bucket and upload the sample data:

```bash
# Make the script executable
chmod +x setup-sample-data.sh

# Run the setup script
./setup-sample-data.sh my-company-qbusiness-docs us-east-1
```

### Manual Setup
If you prefer to set up manually:

```bash
# Create S3 bucket
aws s3 mb s3://my-company-qbusiness-docs --region us-east-1

# Upload files with metadata
aws s3 cp policies/employee-handbook.md s3://my-company-qbusiness-docs/policies/employee-handbook.md \
  --metadata "department=Human Resources,document_type=Policy,confidentiality=Internal"

aws s3 cp procedures/it-security-procedures.md s3://my-company-qbusiness-docs/procedures/it-security-procedures.md \
  --metadata "department=Information Technology,document_type=Procedure,confidentiality=Internal"

# Continue for all files...
```

## Testing Q Business

Once your Q Business application is deployed and the data source sync is complete, try these sample queries:

### Policy Questions
- "What is our expense policy for meals?"
- "How much can I spend on hotel rooms?"
- "What are the company benefits?"
- "What is our code of conduct?"

### Procedure Questions
- "How do I reset my password?"
- "What are the password requirements?"
- "How do we handle security incidents?"
- "What is our data classification policy?"

### Process Questions
- "How do new engineers get onboarded?"
- "What tools do developers use?"
- "What is our Git workflow?"
- "How do we conduct code reviews?"

### Support Questions
- "What are your business hours?"
- "How do I contact customer support?"
- "How do I export my data?"
- "What payment methods do you accept?"

## Customizing the Data

To customize this sample data for your organization:

1. **Replace Content**: Update the documents with your actual policies and procedures
2. **Add Documents**: Include additional file types (PDF, DOCX, TXT)
3. **Update Metadata**: Modify department names and document types to match your organization
4. **Organize Structure**: Reorganize folders to match your company's document hierarchy

## File Formats Supported

The Q Business Enterprise template is configured to index these file types:
- Markdown files (*.md)
- PDF documents (*.pdf)
- Word documents (*.docx)
- Text files (*.txt)

## Metadata Schema

The sample data uses this metadata schema:

```json
{
  "department": "string",      // Department owning the document
  "document_type": "string",   // Type of document
  "confidentiality": "string", // Security classification
  "last_modified": "date"      // Last modification date
}
```

This metadata enables advanced search and filtering capabilities in Q Business.

## Next Steps

1. Run the setup script to create your S3 bucket and upload sample data
2. Deploy the QBusinessEnterprise.yaml CloudFormation template
3. Wait for the initial data source sync to complete (check CloudWatch logs)
4. Access the Q Business web experience and test with sample queries
5. Replace sample data with your actual company documents

For detailed deployment instructions, see [README-Enterprise.md](../README-Enterprise.md).
