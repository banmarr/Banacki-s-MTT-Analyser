import pandas as pd
import sys
import statistics as stats
from datetime import datetime

def main():
    #define constants;
    N = 3 #number of wells with the same treatment adjacent to each other on the plates
    T = 6 #number of treatments on the plates
    R = 3 #number of repeats of the same series on the plates (may be one)
    EMPTY_SEPARATES = True #An empty cell will start a new series if true, not if false
    cur_time = str(datetime.now().strftime("%Y-%m-%d %H-%M-%S")) #get date and time

    #how many plates?
    plate_number = input("How many plates do you want to analyse: 1 or 2? ")
    if plate_number == "2" or "two" in plate_number.lower():

        #check if right argument count
        if len(sys.argv) != 3:
            raise Exception("Invalid number of arguments; 1st argument - research sample")
        
        column_names = ['1','2','3','4','5','6','7','8','9','10','11','12']
        #read research and control plates into dataframe
        r_file = pd.read_csv(sys.argv[1], header=None, names=column_names, sep=';')
        c_file = pd.read_csv(sys.argv[2], header=None, names=column_names, sep=';')
        
        #check if file dimensions proper
        if len(r_file)!=16 or len(r_file.columns)!=12 or len(c_file)!=16 or len(c_file.columns)!=12:
            raise Exception("Invalid dimensions; results must both be from a 64-well plate.")

        #from research and control remove background in the same pd
        r_file = remove_background(r_file)
        c_file = remove_background(c_file)

        #from research and control define how many wells are empty from the right from each row, leaving on the wrong number provided:
        r_empty_row_ids = []
        for i in range(8):
            temp = get_int("On your first (research) plate, how many wells are empty in the row "+str((i+1))+" of your sample plate? WARNING: The program assumes the wells from the right are empty. Every row needs to have only whole repeats on it.")
            if temp > 12 or temp < 0 or (12 - temp) % N != 0:
                raise Exception("Invalid number of empty wells provided.")
            if temp == 12:
                r_empty_row_ids.append(i)
            #put "0" into the  cells, from the right
            for k in range(temp):
                r_file.iat[i, 11-k] = 0
        
        c_empty_row_ids = []
        for i in range(8):
            temp = get_int("On your second (control) plate, how many wells are empty in the row "+str((i+1))+" of your sample plate? WARNING: The program assumes the wells from the right are empty. Every row needs to have only whole repeats on it.")
            if temp > 12 or temp < 0 or (12 - temp) % N != 0:
                raise Exception("Invalid number of empty wells provided.")
            if temp == 12:
                c_empty_row_ids.append(i)
            #put "0" into the  cells, from the right
            for k in range(temp):
                c_file.iat[i, 11-k] = 0

        #remove empty rows from research, add new index to research
        r_file = remove_empty(r_file, r_empty_row_ids)
        c_file = remove_empty(c_file, c_empty_row_ids)
        
        #create names of treatments (treatment1, treatment2 etc.)
        treatment_names = []
        for i in range(T):
            temp = "treatment" + str(i)
            treatment_names.append(temp)

        #create means for research
        #declare variables needed for means for research and control
        r_dict_means = {key:[] for key in treatment_names} #dict of means of research
        r_dict_sds = {key:[] for key in treatment_names} #dict of sds of research
        c_dict_means = {key:[] for key in treatment_names}
        c_dict_sds = {key:[] for key in treatment_names} #dict of sds of research
        
        #iterate through the dataframes, noting means and sds of every 3 wells unless 3 wells are empty 
        r_dict_means = iterate_mean(r_file, r_dict_means, N, T)
        r_dict_sds = iterate_sds(r_file, r_dict_sds, N, T)
        c_dict_means = iterate_mean(c_file, c_dict_means, N, T)
        c_dict_sds = iterate_sds(c_file, c_dict_sds, N, T)

        #check if each dict has as many results as there are repeats on the plate in research and control
        check_result_dicts(r_dict_means, T, R)
        check_result_dicts(r_dict_sds, T, R)
        check_result_dicts(c_dict_means, T, R)
        check_result_dicts(c_dict_sds, T, R)
                    
        #get means of all means noted in research and control
        r_dict_means = get_true_mean(r_dict_means, T, EMPTY_SEPARATES)
        c_dict_means = get_true_mean(c_dict_means, T, EMPTY_SEPARATES)

        #get means of all sds noted in research and control
        r_dict_sds = get_true_sd(r_dict_sds, T, EMPTY_SEPARATES)
        c_dict_sds = get_true_sd(c_dict_sds, T, EMPTY_SEPARATES)

        #get viability % relative to the treatment0 for research and control
        r_dict_relp = {key:None for key in treatment_names}
        r_dict_relp = get_viability(r_dict_relp, r_dict_means, T)
        c_dict_relp = {key:None for key in treatment_names}
        c_dict_relp = get_viability(c_dict_relp, c_dict_means, T)
        
        #create new dataframes for research and control, "r_results" and "c_results", with columns: treatment_name, mean, standard deviation, relative living
        r_results = get_results(treatment_names, r_dict_means, r_dict_sds, r_dict_relp)
        c_results = get_results(treatment_names, c_dict_means, c_dict_sds, c_dict_relp)


        #compare research versus control
        joined_dict_results = {"Treatment name" : treatment_names , "Mean_research" : list(r_dict_means.values()) , "Mean_control" : list(c_dict_means.values()), "Viability_research" : list(r_dict_relp.values()), "Viability_control" : list(c_dict_relp.values())}
        joined_results =  pd.DataFrame.from_dict(joined_dict_results)
        joined_results["Mean_research/control [%]"] = (joined_results["Mean_research"] / joined_results["Mean_control"]) * 100
        joined_results["Viability_research/control [%]"] = (joined_results["Viability_research"] / joined_results["Viability_control"]) * 100


        r_path = r'C:\Users\Marcin\project\output_research_'+cur_time+'.csv'
        c_path = r'C:\Users\Marcin\project\output_control_'+cur_time+'.csv'
        joined_path = r'C:\Users\Marcin\project\output_control_'+cur_time+'.csv'
        
        r_results.to_csv(r_path, sep=";", index=False)
        print("Research plate statistics are:")
        print(r_results.to_string())
        c_results.to_csv(c_path, sep=";", index=False)
        print("Control plate statistics are:")
        print(c_results.to_string())
        joined_results.to_csv(joined_path, sep=";", index=False)
        print("Research side by side with control:")
        print(joined_results.to_string())
    
    elif plate_number == "1" or "one" in plate_number.lower():

        #check if right argument count
        if len(sys.argv) != 2:
            raise Exception("Invalid number of arguments; 1st argument - research sample")
        
        column_names = ['1','2','3','4','5','6','7','8','9','10','11','12']
        #read research plate into dataframe
        r_file = pd.read_csv(sys.argv[1], header=None, names=column_names, sep=';')
        
        #check if file dimensions proper
        if len(r_file)!=16 or len(r_file.columns)!=12:
            raise Exception("Invalid dimensions; results must both be from a 64-well plate.")

        #from research remove background in the same pd
        r_file = remove_background(r_file)

        #from research define how many wells are empty from the right from each row, leaving on the wrong number provided:
        r_empty_row_ids = []
        for i in range(8):
            temp = get_int("How many wells are empty in the row "+str((i+1))+" of your sample plate? WARNING: The program assumes the wells from the right are empty. Every row needs to have only whole repeats on it.")
            if temp > 12 or temp < 0 or (12 - temp) % N != 0:
                raise Exception("Invalid number of empty wells provided.")
            if temp == 12:
                r_empty_row_ids.append(i)
            #put "0" into the  cells, from the right
            for k in range(temp):
                r_file.iat[i, 11-k] = 0
        

        #remove empty rows from research, add new index to research
        r_file = remove_empty(r_file, r_empty_row_ids)
        
        #create names of treatments (treatment1, treatment2 etc.)
        treatment_names = []
        for i in range(T):
            temp = "treatment" + str(i)
            treatment_names.append(temp)

        #declare variables needed for means for research
        r_dict_means = {key:[] for key in treatment_names} #dict of means of research
        r_dict_sds = {key:[] for key in treatment_names} #dict of sds of research
        
        #iterate through the dataframes, noting means and sds of every 3 wells unless 3 wells are empty 
        r_dict_means = iterate_mean(r_file, r_dict_means, N, T, EMPTY_SEPARATES)
        r_dict_sds = iterate_sds(r_file, r_dict_sds, N, T, EMPTY_SEPARATES)

        #check if each dict has as many results as there are repeats on the plate in research
        check_result_dicts(r_dict_means, T, R)
        check_result_dicts(r_dict_sds, T, R)
                    
        #get means of all means noted in research
        r_dict_means = get_true_mean(r_dict_means, T)

        #get means of all sds noted in research
        r_dict_sds = get_true_sd(r_dict_sds, T)

        #get viability % relative to the treatment0 for research
        r_dict_relp = {key:None for key in treatment_names}
        r_dict_relp = get_viability(r_dict_relp, r_dict_means, T)
        
        #create new dataframe for research, "r_results", with columns: treatment_name, mean, standard deviation, relative living
        r_results = get_results(treatment_names, r_dict_means, r_dict_sds, r_dict_relp)

        r_path = r'C:\Users\Marcin\project\output_'+cur_time+'.csv'

        r_results.to_csv(r_path, sep=";", index=False)
        print(r_results.to_string())
        
    
    else:
        raise Exception("Invalid number provided; acceptable input: '1', '2', 'one', 'two'.")



def get_int(question): #based on https://stackoverflow.com/questions/8075877/converting-string-to-int-using-try-except-in-python
    try:
        print(f"{question}")
        inty_temp = int(input())
        return inty_temp
    except ValueError:
        print ("Please provide a number")
        get_int(question)




def remove_background(dataframe):
    for b in range(0, 16, 2):
        dataframe.iloc[b] = dataframe.iloc[b] - dataframe.iloc[b+1]
    #remove background rows from research
    dataframe.drop(dataframe.index[[1, 3, 5, 7, 9, 11, 13, 15]], inplace=True)
    #change row indexes in research
    new_index=pd.Index([0,1,2,3,4,5,6,7])
    dataframe.set_index(new_index, inplace=True)
    return dataframe




def remove_empty(frame, listy):
    listy = pd.Index(listy)
    frame.drop(frame.index[(listy)], inplace=True)
    frame.set_index(pd.Index(list(range(len(frame)))), inplace=True)
    return frame




def iterate_mean(framey, dict_means, repeat_number, repeat_plate_number, marker):
    oper_list = []
    z = 0
    for i in range(len(framey)):
        for k in range(len(framey.columns)):
            if len(oper_list) == repeat_number:
                if oper_list[0] == 0 and len(set(oper_list)) == 1:
                    oper_list = []
                    oper_list.append(framey.iat[i, k])
                    if marker == True:
                        z = 0
                else:
                    dict_means["treatment"+str(z)].append(stats.mean(oper_list))
                    oper_list = []
                    oper_list.append(framey.iat[i, k])
                    z = z + 1
                    if z > repeat_plate_number - 1:
                        z = 0
            else:
                oper_list.append(framey.iat[i, k])
    return dict_means




def iterate_sds(framey, dict_sds, repeat_number, repeat_plate_number, marker):
    oper_list = []
    z = 0
    for i in range(len(framey)):
        for k in range(len(framey.columns)):
            if len(oper_list) == repeat_number:
                if oper_list[0] == 0 and len(set(oper_list)) == 1:
                    oper_list = []
                    oper_list.append(framey.iat[i, k])
                    if marker == True:
                        z = 0
                else:
                    dict_sds["treatment"+str(z)].append(stats.stdev(oper_list))
                    oper_list = []
                    oper_list.append(framey.iat[i, k])
                    z = z + 1
                    if z > repeat_plate_number - 1:
                        z = 0
            else:
                oper_list.append(framey.iat[i, k])
    return dict_sds




def check_result_dicts(dict, repeat_plate_number, onplate_repeats):
    for i in range(repeat_plate_number):
        if len(dict["treatment"+str(i)]) != onplate_repeats:
            raise Exception("Unable to execute; there is other number of repeats than stated in the beginning of the code")




def get_true_mean(dict, repeat_plate_number):
    for i in range(repeat_plate_number):
        dict["treatment"+str(i)] = stats.mean(dict["treatment"+str(i)])
    return dict 

def get_true_sd(dict, repeat_plate_number):
    for i in range(repeat_plate_number):
        dict["treatment"+str(i)] = stats.mean(dict["treatment"+str(i)])
    return dict




def get_viability(dict_viability, dict_means, repeat_plate_number):
    for i in range(repeat_plate_number):
        if i == 0:
            dict_viability["treatment0"] = 100
        else:
            dict_viability["treatment"+str(i)] = (dict_means["treatment"+str(i)] / dict_means["treatment0"]) * 100
    return dict_viability




def get_results(names_list, dict_means, dict_sds, dict_viability):
    dict_results = {"Treatment name": names_list, "mean":list(dict_means.values()), "SD":list(dict_sds.values()), "Viability (rel. to control)":list(dict_viability.values())}
    return pd.DataFrame.from_dict(dict_results)




main()