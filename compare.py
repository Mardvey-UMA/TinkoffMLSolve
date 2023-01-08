import ast, re, pathlib, shutil, pathlib
import numpy as np
import argparse

def remove_comments(source): #Функция для удаления однострочных комментариев 
    string = re.sub(re.compile("'''.*?'''", re.DOTALL), "", source)  
    string = re.sub(re.compile('""".*?"""', re.DOTALL), "", source)  
    string = re.sub(re.compile("(?<!(['\"]).)#[^\n]*?\n"), "\n", string) 
    return string 

def make_clean_ast(pyfile_path1, pyfile_path2):
    """
    Аргументы: Абсолютный путь до первого и второго Python кода соотвественно
    Возвращает: Отформатированное абстрактное синтаксическое дерево, для дальнейшего сравнения
    """
    signs = [']','[','(',')',',',"'"] 
    #Происходит копирование входных файлов, для последующей генерации из них текстовых файлов
    new_name1 = pyfile_path1[:-3] + 'copy1' + '.py'
    new_name2 = pyfile_path2[:-3] + 'copy2' + '.py'

    shutil.copyfile(pyfile_path1, new_name1)
    shutil.copyfile(pyfile_path2, new_name2)

    new_name1 = pathlib.Path(new_name1)
    new_name2 = pathlib.Path(new_name2)
    
    new_path = str([part + '/' for part in list(str(new_name1).split('/')[:-1])]).replace(']','').replace('[','').replace(',','').replace("'",'').replace(' ','')
    new_name1.rename(new_path + 'copy1' + '.txt')
    copy1 = new_path + 'copy1' + '.txt'
    new_path = str([part + '/' for part in list(str(new_name2).split('/')[:-1])]).replace(']','').replace('[','').replace(',','').replace("'",'').replace(' ','')
    new_name2.rename(new_path + 'copy2' + '.txt')
    copy2 = new_path + 'copy2' + '.txt'
    #Конец конвертации файлов

    f = open(copy1) #Открытие текстового файла с исходным кодом
    code1 = ""
    for line in f:
        code1+=line
    code1 = remove_comments(code1) #Удаление комментариев
    tree1 = ast.parse(source = code1) #Построение абстрактного синтаксического дерева с помощью библиотеки AST
    ast_code1 = ast.dump(tree1, annotate_fields=False) #Конвертация дерева, в строку, аннотации удаляются, за ненадобностью
    #Нормализация дерева, удаление скобок кавычек и лишних пробелов
    for g in signs:
        ast_code1 = ast_code1.replace(g,' ')
    ast_code1 = re.sub(r" [\d+] ", "", ast_code1)
    ast_code1 = re.sub(" +", " ", ast_code1)
    # Переменная ast_code* хранит строку в ввиде нормализованного синтаксического дерева
    # Над вторым файлом производятся аналогичные манипуляции
    f = open(copy2)
    code2 = ""
    for line in f:
        code2+=line   
    code2 = remove_comments(code2)
    tree2 = ast.parse(source = code2)
    ast_code2 = ast.dump(tree2, annotate_fields=False)
    for g in signs:
        ast_code2 = ast_code2.replace(g,' ')
    ast_code2 = re.sub(r" [\d+] ", "", ast_code2)
    ast_code2 = re.sub(" +", " ", ast_code2)
    
    
    return ast_code1, ast_code2

def jaccard(s1, s2):
    """
    Алгоритм Джаккарда
    """
    s1 = set(s1.split(' '))
    s2 = set(s2.split(' '))
    inter = s1.intersection(s2)
    union = s1.union(s2)
    return len(inter) / len(union)

def levenstin(s1, s2):
    """
    Расстояние Левенштейна, сравнение посимвольно
    """
    lev = np.zeros((len(s1), len(s2)))
    for i in range(len(s1)):
        for j in range(len(s2)):
            if (min(i, j) == 0):
                lev[i, j] = max(i, j)
            else:
                x = lev[i-1, j] 
                y = lev[i, j-1] 
                z = lev[i-1, j-1]  
                lev[i, j] = min([x, y, z])
                if s1[i] != s2[j]:
                    lev[i, j] += 1  
    res = (1 - (lev[-1,-1])/(max(len(s1),len(s2))))
    return res

def levenstin_w(s1, s2):
    """
    Расстояние Левенштейна, сравнение по словам
    """
    s1 = s1.split(' ')
    s2 = s2.split(' ')
    lev = np.zeros((len(s1), len(s2)))
    for i in range(len(s1)):
        for j in range(len(s2)):
            if (min(i, j) == 0):
                lev[i, j] = max(i, j)
            else:
                x = lev[i-1, j] 
                y = lev[i, j-1] 
                z = lev[i-1, j-1]  
                lev[i, j] = min([x, y, z])
                if s1[i] != s2[j]:
                    lev[i, j] += 1
    res = (1 - (lev[-1,-1])/(max(len(s1),len(s2))))
    return res 
#Реализация консольного интерфейса
parser = argparse.ArgumentParser()
parser.add_argument('indir', type=str)
parser.add_argument('outdir', type=str)
args = parser.parse_args()
input_path = args.indir
output_path = args.outdir
#Открытие файлов для записи и чтения
source = open(input_path, 'r')
result = open(output_path, 'w')

for line in source:
    path1, path2 = list(map(str, line.split()))
    code_ast1, code_ast2 = make_clean_ast(path1, path2)
    avg_res = (jaccard(code_ast1, code_ast2) + levenstin(code_ast1, code_ast2) + levenstin_w(code_ast1, code_ast2)) / 3
    result.write(str(avg_res) + '\n')
    
    
