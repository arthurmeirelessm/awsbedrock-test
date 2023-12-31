import io
import json
import boto3
from googletrans import Translator
from PyPDF2 import PdfReader
import config

bedrock = boto3.client('bedrock' , 'us-west-2', endpoint_url='https://bedrock.us-west-2.amazonaws.com')

translator = Translator()

s3 = boto3.client(
    's3',
    "us-east-2",
    aws_access_key_id="AKIAYH6IOHMRB5L2DZRR",
    aws_secret_access_key="/hHXcvWsp8l+/DHCdOTjVEh2SSb2mvunmlobxXl5"
)

# Usando o BedRock no modelo Titan para extrair palavras-chave
 
def get_completion(prompt, max_tokens_to_sample):
    
    body = json.dumps({
        "prompt": prompt,
        "max_tokens_to_sample": max_tokens_to_sample,
        "temperature": 1,
        "top_k": 250,
        "top_p": 0.999,
        "stop_sequences": ["\nHuman:"],
        "anthropic_version": "bedrock-2023-05-31"
    })

    modelId = 'anthropic.claude-v2'
    accept = 'application/json'
    contentType = 'application/json'

    response = bedrock.invoke_model(
        body=body,
        modelId=modelId,
        accept=accept,
        contentType=contentType
    )

    response_body = json.loads(response.get('body').read())
    completion = response_body.get('completion')
    return completion

# ------------------------------------------------------------------------------------------------------------------

# lendo e traduzindo os objetos (PDFs) que estão no bucket "bedrock-tests-bucket"

bucket_name = "bedrock-tests-bucket"
translated_pages = []
folder_name = 'extraction_data'

result_dict = {}
document_result = {}
result_append = {}
final_result = {}

for obj in s3.list_objects_v2(Bucket=bucket_name, Prefix=f"{folder_name}/").get("Contents", []):
        if obj["Size"] == 0:
            continue
        file_content = s3.get_object(Bucket=bucket_name, Key=obj['Key'])['Body'].read()
        pdf_reader = PdfReader(io.BytesIO(file_content))
        

        
        for page_number, page in enumerate(pdf_reader.pages, start=1):
            page_text = page.extract_text()
            prompt = f"""Human: {config.prompt_data} + {page_text}
            Assistant:
            """
            result_text = get_completion(prompt, 8191)
            
            document_result[f"Página {page_number}"] = result_text.strip()
            
        result_dict[obj['Key']] = document_result
        
        print(result_dict)    
        for keyword in config.keywords:
                if keyword in result_dict:
                    value = result_text.split(keyword, 1)[1].strip()
                    if value != None:
                        result_append[keyword].append(value)
    
# Atualize o dicionário de resultados geral com os resultados deste documento
        print(result_append)
        for keyword, values in result_append.items():
            if values:
                final_result[keyword] = values

# Converta o dicionário de resultados em JSON e imprima
result_json = json.dumps(final_result, indent=2)
print(result_json)



    



