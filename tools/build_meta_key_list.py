import sys, os, inspect, pkgutil, json, csv
from collections.abc import Iterable
from importlib import import_module
from pydantic import BaseModel, Field, AliasChoices, AliasPath, validator

#Pull in models module
app_path = os.path.realpath(os.path.join(os.path.dirname(__file__),'..','app')) 
sys.path.append(app_path)
import api.models

def collapse_alias_path(path): 
    """
    Accepts either an array of AliasPaths or a single AliasPath and converts a unique list of options
    """
    alias_list = set()
    
    if isinstance(path,Iterable):   
        for p in path:
            for option in p.path:
                alias_list.add(option)
    else: 
        for option in path.path:
            alias_list.add(option)
    return [a for a in alias_list]
    
def convert_to_json_encodable_values(val): 
    """
    Converts AliasPath and AliasChoices into JSON encodable values
    """
    if isinstance(val, AliasPath):
        return collapse_alias_path(val)
    elif isinstance(val, AliasChoices):
        return val.choices
    else:
        raise TypeError('convert_to_json_encodable_values',f'unexpected type {type(val)}',val)

def build_meta_key_list(model): 
    """
    Returns the interesting attributes of a pydantic model into a dict
    """
    fields = model.model_fields
    field_details = []
    for k,v in fields.items():
        d = {
            'name':k,
        }
        
        if v.alias:
            d['alias'] = v.alias
                
        if v.is_required: 
            d['required'] = v.is_required()
        
        if v.validation_alias:
            d['validation'] = v.validation_alias
        
        field_details.append(d)

    return field_details
    
def find_models():
    """
    Loads in all sub modules for api.models and scans for all pydantic models. Converts any discovered models into a dict
    """
    model_details = {}
    for mod in pkgutil.iter_modules(api.models.__path__): 
        print(f"Scaning api.models.{mod.name}")
        target_import = import_module(f"api.models.{mod.name}")
        target_models = [tar for tar in inspect.getmembers(target_import,inspect.isclass) if issubclass(tar[1],BaseModel)]
        
        target_model_details = []
        for target in target_models: 
            target_model_details.append(
                {
                'module':mod.name,
                'model':target[0],
                'fields':build_meta_key_list(target[1])
                }
            )
        
        model_details[mod.name] = {
            'models': target_model_details
        }
        
    return model_details
       
def build_csv(model_details): 
    with open('report.csv','w') as report_stream: 
        report_writer = csv.writer(report_stream, delimiter=',')
        
        report_writer.writerow([
            'Module',
            'Model',
            'Field',
            'Alias',
            'Fallback',
            'Required'
        ])
    
    
        for module, details in model_details.items(): 
            for model in details['models']:
                for field in model['fields']: 
                    
                    fallback = ''
                    alias = ''
                    
                    if 'alias' in field: 
                        if(isinstance(field['alias'],AliasChoices)):
                            alias = field['alias'].choices[0]
                            fallback = field['alias'].choices[1]
                        else: 
                            alias = field['alias']
                    
                    report_writer.writerow(
                     [
                         module,
                         model['model'],
                         field['name'],
                         alias, 
                         fallback,
                         field['required']
                         
                     ]   
                    )

def build_json(model_details): 
    with open('test.json','w') as dump:
        dump.write(json.dumps(model_details,indent=4, default=convert_to_json_encodable_values))

if __name__ == "__main__": 
    model_details = find_models()
    build_csv(model_details)
    #print(model_details)