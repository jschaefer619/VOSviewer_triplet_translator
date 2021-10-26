#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import json
import re
import random
import argparse
import os

def main() -> None:
    """Entrypoint of Program Run as Module"""
    ...

def read_args():

    parser = argparse.ArgumentParser()
    parser.add_argument( "node_col_name_1", type=str, help="column name of input file to be represented as node (first of two inputs)")
    parser.add_argument( "edge_col_name", type=str, help="column name of input file to be represented as edges (first of one input)")
    parser.add_argument( "node_col_name_2", type=str, help="column name of input file to be represented as node (second of two inputs)")
    parser.add_argument("-i", "--input_filename", type=str, help=".csv input filepath to translate into VOSviewer triplets")
    parser.add_argument("-c", "--context_col_name", type=str, default="texts", help="column file to be represented as context")
    parser.add_argument("-v", "--verbosity", action="count", default=0)
    parser.add_argument("-o", "--output", type=str, default=os.path.join(dir, 'output', 'output.json'), help="argument for specifying output filepath location")
    parser.add_argument("-f", "--include_formatted_html", action="count", default=0, help="argument to determine if metadata should be included & description formatted specific to Discrimination Triplets")

    args = parser.parse_args()

    if args.input_filename == None:
        default_path = os.path.join(dir, 'data', 'antisemitism_discrimination_triplets.csv')
        print("No explicitly specified input filepath. Using default input filepath: " + default_path)
        args.input_filename = default_path

    if os.path.exists(args.input_filename) == False: # specified or default filepath does not exist

        print("Filepath not found.")
        potential_files = os.listdir(os.path.join(dir, 'data'))    
        csv_files = list(filter(lambda f: f.endswith('.csv'), potential_files))

        print("Searching through data directory for valid input file...")
        if len(csv_files) >= 0:

            found_file = False
            for input_filepath in csv_files:

                new_path = os.path.join(dir, 'data', input_filepath)
                
                print("Run Program on this filepath: " + new_path + " ? (y/n)")
                user_input = input()

                if user_input[0] == 'Y' or user_input[0] == 'y':
                    args.input_filename = new_path
                    found_file = True
                    break
                else:
                    continue

            if found_file == False:
                print("No more valid input files. Exiting Program")
                exit()

        else:
            print("Exiting Program")
            exit()

    return {
        "file_path" : args.input_filename,
        "node_column_names" : [args.node_col_name_1, args.node_col_name_2],
        "edge_column_name" : args.edge_col_name,
        "context_column_name" : args.context_col_name,
        "output_path" : args.output,
        "verbosity": args.verbosity,
        "include_formatted_html" : args.include_formatted_html
    }

def extract_int_code(file_name):
    int_code = file_name.split('-')[0][:-1]
    return int_code

def make_html(drive_id):
    return 'https://drive.google.com/uc?export=view&id=' + str(drive_id)

def clean_text (input_text):
    try:
        input_text = input_text.lower() # lowercase the text
        input_text = input_text.strip() # remove any excess spaces around text
        input_text = input_text.capitalize() # capitalize first letter
        return input_text
    except AttributeError:
        return input_text

def configure_metadata(df_input):

    try:
        filename = os.path.join(dir, 'description_metadata', 'drive_ids.csv')
        drive_ids = pd.read_csv(filename) # need to make this flexible to provide custom drive ids
    except:
        print("Error reading google drive id file. Exiting Program")

    drive_ids['int_code'] = [extract_int_code(x) for x in drive_ids['file_name']]

    drive_ids['drive_id'] = drive_ids['drive_id'].astype('str')
    drive_ids['int_code'] = drive_ids['int_code'].astype('int64')
    drive_ids.drop_duplicates(subset='int_code')

    drive_ids_ = []

    for row in df_input.itertuples():
        if row.intcode in drive_ids['int_code'].to_list():
            drive_ids_.append(drive_ids[drive_ids['int_code'] == row.intcode]['drive_id'].values[0])
        else:
            drive_ids_.append('nan')
            
    df_input['drive_id'] = drive_ids_

    df_input['image_link'] = [make_html(x) for x in df_input['drive_id']]
    df_input[df_input['image_link'] == 'https://drive.google.com/file/d/nan/view']['image_link'] = "https://via.placeholder.com/100.png?text=Speaker+Picture"


    corrected_link = []

    for value in df_input['image_link']:
        if value == 'https://drive.google.com/uc?export=view&id=nan':
            corrected_link.append('https://via.placeholder.com/100.png?text=Speaker+Picture')
        else:
            corrected_link.append(value)
            
    df_input['image_link'] = corrected_link

    corrected_URL = []
    testimony_id = []

    for row in df_input.itertuples():
        if pd.isna(row.segment) == False:
            
            testimony_id.append(row.URL.split('&')[0].split('=')[1])
            url = row.URL.split('&')[0]
            url = url + '&segmentNumber=' + str(row.segment)
            corrected_URL.append(url)
        else:
            corrected_URL.append(row.URL.split('&')[0])


    df_input['URL'] = corrected_URL
    df_input['testimony_id'] = testimony_id

    df_input['image_link'].to_list()

    return df_input

def format_dataframe(df, path):
        
        df['subjects_coref'] = [clean_text(x) for x in df['subjects_coref']]
        df['objects_coref'] = [clean_text(x) for x in df['objects_coref']]
        
        # get all of the entities from the corpus
        all_entities = df['subjects_coref'].append(df['objects_coref'])

        # eliminate duplicate entry
        all_entities = all_entities.drop_duplicates()

        # reset index, use index of unique entities as id
        all_entities = all_entities.reset_index(drop=True)
        all_entities.index = range(1,len(all_entities)+1)
        
        # first generate the nodes by finding unique entities in the spreadsheet...
        entity_list_to_convert = []
        
        filename = os.path.join(dir, 'description_metadata', 'contraction.csv')
        contractions = pd.read_csv(filename)
        contractions = dict(zip(contractions.extended, contractions.contraction))
        
        filename = os.path.join(dir, 'description_metadata', 'manual_relation_corrections.csv')
        manual_corrections = pd.read_csv(filename)
        manual_corrections = dict(zip(manual_corrections.full_text, manual_corrections.manual_corrections))
            
        def make_heading_html(text):
            return "<div class='description_heading'>" + text + "</div>"
        def make_formatted_text_html(text, relation):
            
            relation = relation.strip()
            context = text.split(relation)
            
            if len(context) == 1:
                # search for a contraction
                for extended in contractions.keys():
                    if extended in relation:
                        relation = contractions[extended] # replace extended phrase with contraction of extended
                        context = text.split(relation)
                        break
                        
                if len(context) == 1:
                    # search for manual corrections...
                    for full_text in manual_corrections.keys():
                        if full_text == text or full_text in text:
                            relation = manual_corrections[full_text]
                            context = text.split(relation)  
            try:
                return '<div class="basic_text" >' + context[0] + "<b>" + relation + "</b>" + context[1] + "</div>"
            except TypeError:
                return ""
            except IndexError:
                return '<div class="basic_text" >' + text + "</div>"
        def make_label_html(text):
            return "<div class='description_label'>" + text + "</div>"
        def make_link_html(text, link):
            return "<a class='description_url' href='" + link + "'>{" + text + "}</a>"
        def make_specialized_triplet(df):
            output = ''
            for row in df.itertuples():
                output = output + ("<div class='description_heading'><a class='description_url' href='" + row.URL + "'> " + row.full_name + " </a></div>" + '<img src=' + row.image_link + ' width="200px" height="auto">' 
                                + make_heading_html('Context: ') + make_formatted_text_html(row.texts, row.relations) + "<hr>")
            output = output[:-4]
            return output

        def make_generic_triplet(df):

            for row in df.itertuples():            
                output = ''
                output = output + ('<div class="basic_text" >' + "<b>" + str(args_dict["node_column_names"][0]) + ": " + "</b>" + row.subjects_coref + "</div>" +
                               '<div class="basic_text" >' + "<b>" + str(args_dict["edge_column_name"]) + ": " + "</b>" + row.relations + "</div>" +  
                               '<div class="basic_text" >' + "<b>" + str(args_dict["node_column_names"][1]) + ": " + "</b>" + row.objects_coref + "</div>")
                try:
                    output = output + '<div class="basic_text" >' +  "<b>" + str(args_dict['context_column_name']) + ": " + "</b>" + str(row.texts) + "</div>"
                except:
                    pass

                output = output + "<hr>"

            output = output[:-4]
            return output

        # make descriptions for each entity
        for entity in all_entities:
            if (pd.isna(entity) == True):
                continue
                
            sample_triplets = df[(df['subjects_coref'] == entity) | (df['objects_coref'] == entity)]
            sample_triplets = sample_triplets.sample(frac=1, random_state=0)
            sample_triplets = sample_triplets.head(3) # only sample the top 3 entities

            entity_to_convert = {
                "id": int(all_entities[all_entities == entity].index[0]),
                "label": str(entity),
                "weights": {
                    "Documents": 1, #len(df[df['subjects_coref'] == entity]),  number of times entity appeared in subset relations (could incorporate global metrics)
                    "Citations": 1 #len(df[df['subjects_coref'] == entity])  same as above, but number of relations 
                }
            }
            if args_dict['include_formatted_html'] >= 1:
                entity_to_convert["description"] = '<div class="content-box">' + "<div class='description_heading'> Sample Triplets: {label} </div>" + make_specialized_triplet(sample_triplets) + '</div>',
            else:
                entity_to_convert["description"] = '<div class="content-box">' + "<div class='description_heading'> Sample Triplets: {label} </div>" + make_generic_triplet(sample_triplets) + '</div>',

            entity_list_to_convert.append(entity_to_convert)

        items = entity_list_to_convert
        
        # generate descriptions for each link; should look into implementing protocol for looking at duplicate instances
        df_dedupe = df.drop_duplicates(subset=['subjects_coref', 'relations', 'objects_coref'])
        links = []
  
        for row in df_dedupe.itertuples():

            if (pd.isna(row.subjects_coref) == True or pd.isna(row.objects_coref) == True):
                continue
                
            try:               
                link_python = {
                    "source_id" : int(all_entities[all_entities == row.subjects_coref].index[0]),
                    "target_id" : int(all_entities[all_entities == row.objects_coref].index[0]),
                    "strength" : 1 #len(df[(df['subjects_coref'] == row.subjects_coref) & (df['objects_coref'] == row.objects)]),
                }
                if args_dict['include_formatted_html'] >= 1: # bespoke formatting
                    link_python["description"] = ('<div class="content-box">' + "<div class='description_heading'><a class='description_url' href='" + row.URL + "'> " + row.full_name + " </a></div>" + '<img src=' + row.image_link + ' width="200px" height="auto">'
                                            + make_heading_html('Context: ') + make_formatted_text_html(row.texts, row.relations) + '</div>')
                else: # generic formatting
                    output = ('<div class=basic_text >' + "<b>" + str(args_dict["node_column_names"][0]) + ": " + "</b>" + row.subjects_coref + "</div>" +
                           '<div class="basic_text" >' + "<b>" + str(args_dict["edge_column_name"]) + ": " + "</b>" + row.relations + "</div>" +  
                           '<div class="basic_text" >' + "<b>" + str(args_dict["node_column_names"][1]) + ": " + "</b>" + row.objects_coref + "</div>")
                    try: # attempt generic formatting with context
                        output = output + '<div class="basic_text" >' +  "<b>" + str(args_dict['context_column_name']) + ": " + "</b>" + str(row.texts) + "</div>"
                    except AttributeError: # no  context found, omit context
                        pass
                    link_python["description"] = output

            except TypeError:
                continue

            links.append(link_python)

            def make_plural(input_str): # slightly naive way to handle plurals
                if input_str[-1] == 's' or input_str[-1] == 'S':
                    return input_str + 's'
                else :
                    return input_str

        data_struct = {'network': {'items': items, 'links': links}, 
                       'config': {'terminology': {'item' : args_dict["node_column_names"][0] + '/' + args_dict["node_column_names"][1], 'items' : make_plural(args_dict["node_column_names"][0]) + '/' + make_plural(args_dict["node_column_names"][1]), 
                        'link' : args_dict["edge_column_name"], 'links' : make_plural(args_dict["edge_column_name"])},
                        'parameters' : {'item size' : 1}, 
                        'styles' : {'description_heading' : "label: description-heading;\n    color: #757575;\n    font-weight: 600;\n font-size: 1.5em;\n ",
                                   'description_label' : "label: description-label;\n  ",
                                   'description_text ': "label: description-text;\n    margin-bottom: 4px;\n  font-size: 1.25em;\n", # not in use, have been using basic text styling below instead
                                   'basic_text' : "label: basic-text; margin-bottom: 4px;\n  font-size: 1.25em;\n",
                                   'description_url' : '\n    label: description-url;\n    text-decoration: none;\n    color: #1e7896;\n  font-weight: 600;\n font-size: 1.25em;\n '},}
                      }
        output = json.JSONEncoder().encode(data_struct)

        with open(path, 'w') as json_file:
            json.dump(data_struct, json_file)
        

if __name__ == "__main__":

    dir = os.path.dirname(__file__)

    args_dict = read_args()

    try:
        df_input = pd.read_csv(args_dict['file_path'])
    except Exception as e:
        print(e)
        print("Error reading provided input file. Exiting Program")
        exit()

    # easy fix currently, but not very efficient
    df_input['objects_coref'] = df_input[args_dict["node_column_names"][0]]
    df_input['subjects_coref'] = df_input[args_dict["node_column_names"][1]]
    df_input['relations'] = df_input[args_dict["edge_column_name"]]

    try:
        df_input['texts'] = df_input[args_dict["context_column_name"]]
    except KeyError:
        print("Context metadata for triplets not found. Use Argument -c to specify context column within input data (if applicable)")

    if args_dict["include_formatted_html"] >= 1:
        if args_dict['verbosity'] >= 1:
            print('Fetching Metadata for triplets specific to Discrimination Dataset...')
        try:
            df_input = configure_metadata(df_input)
        except Exception as e:
            print(e)
            print("Error fetching metadata for triplets specific to Discrimination Dataset \nBe sure that the input Datatset is formatted in a similar way to Discrimination Dataset, or do not use the -f argument")
            exit()


    if args_dict['verbosity'] >= 1:
        if args_dict["include_formatted_html"] >= 1:
            print("Formatting HTML descriptions specific to Discrimination Dataset...")
        else:
            print("Formatting HTML descriptions for general data")

    try:
        format_dataframe(df_input, args_dict['output_path'])
    except Exception as e:
        print(e)
        print("Error translating Dataset to VOSviewer JSON file")
        exit()

    if args_dict['verbosity'] >= 1:
        out = os.path.basename(args_dict["output_path"])
        print("Finished Task.")








