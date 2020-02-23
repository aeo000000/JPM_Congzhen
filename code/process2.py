# coding: utf-8
import os
import sys

def list_folders_files(path, suffixes_filters = []):
    list_folders = []
    list_files = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            list_folders.append(file)
        else:
            file_ext = os.path.splitext(file)[-1]
            ignore_this_file = 0
            if (suffixes_filters is not None):
                ignore_this_file = 1
                for suffix in suffixes_filters:
                    if (file_ext.upper() == suffix.upper()):
                        ignore_this_file = 0
                        break
            if (ignore_this_file == 0):
                list_files.append(file)
    return (list_folders, list_files)
    

is_normal_chapter = False
chapter_count = 1
split_count = 1
def processTitle(output_buff_array, str_title):
    str_part = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
    
    if (str_title.find('第') >= 0):
        global chapter_count
        global is_normal_chapter
        
        if (((chapter_count - 1) % 10) == 0):
            part_no = (chapter_count - 1) // 10
            part_title = '{\\titlename}卷之%s' % (str_part[part_no])
            part_string = '\\part*{%s}' % part_title
            output_buff_array.append(part_string)
            
            part_string = '\\addcontentsline{toc}{part}{%s}' % part_title
            output_buff_array.append(part_string)
            
            output_buff_array.append('\r\n')
            
        is_normal_chapter = True
        
        pdf_page_string = ('\\includepdf[pages={%d,%d},fitpaper=false]{tst.pdf}' % ((chapter_count - 1) * 2 + 1, (chapter_count - 1) * 2 + 2))
        output_buff_array.append(pdf_page_string)
        chapter_count += 1
    
    insert_string = ('\\chapter*{%s}' % str_title) 
    output_buff_array.append(insert_string)

    insert_string = ('\\addcontentsline{toc}{chapter}{%s}' % str_title) 
    output_buff_array.append(insert_string)

    if (is_normal_chapter):
        part_no = ((chapter_count - 1) + 9) // 10
    
        str_tt = str_part[(part_no - 1)]
        insert_string = ('\\markboth{{\\titlename}卷之%s}{%s}' % (str_tt, str_title))
    else:
        insert_string = ('\\markboth{\\titlename}{%s}' % (str_title))
        
    output_buff_array.append(insert_string)
    output_buff_array.append('\r\n')
                
def processParagraph(input_line_buff, output_buff_array):
    '''
    <p   >
    <span >
    </span>
    <br />
    </p>
    '''
    index = input_line_buff.find('<p', 0)
    index += len('<p')
    
    index2 = input_line_buff.find('>', index)
    if (index2 <= 0):
        return
    
    str_pang_pi = '<span class=\"pz\"><span class=\"ord\">旁<span class=\"ords\">批</span></span>'
    len_pang_pi = len(str_pang_pi)
    
    str_mei_pi  = '<span class=\"pz\"><span class=\"ord\">眉<span class=\"ords\">批</span></span>'
    len_mei_pi  = len(str_mei_pi)

    str_jia_pi  = '<span class=\"pz\"><span class=\"ord\">夹<span class=\"ords\">批</span></span>'
    len_jia_pi  = len(str_jia_pi)
    
    line_buff_dst = ''
    
    input_line_buff = input_line_buff[(index2 + 1) :]
    while (True):
        index1 = input_line_buff.find('<br')
        index2 = input_line_buff.find('<span')
        if ((index1 < 0) and (index2 < 0)):
            index = input_line_buff.find('</p>')
            line_buff_dst += (input_line_buff[ : index])
            break
            
        if (index1 < 0):
            index = index2
        elif (index2 < 0):
            index = index1
        else:
            index = min(index1, index2)
        
        # <br class="calibre1"/>
        if (index == index1):
            line_buff_dst += (input_line_buff[: index1])
            index1 = input_line_buff.find('/>')
            input_line_buff = input_line_buff[(index1 + len('/>')) : ]
            
            # print('found <br')
            
            continue
            
        index = index2    
        index1 = input_line_buff.find(str_pang_pi)
        index2 = input_line_buff.find(str_mei_pi)
        index3 = input_line_buff.find(str_jia_pi)
        if ((index1 == index) or (index2 == index) or (index3 == index)):
            line_buff_dst += (input_line_buff[: index])
            
            len_skip = len_pang_pi
            format_str = '{\\pangpi{%s}}'
            if (index2 == index):
                len_skip = len_mei_pi
                format_str = '{\\meipi{%s}}'
            elif (index3 == index):    
                len_skip = len_jia_pi
                format_str = '{\\jiapi{%s}}'
                
            index4 = input_line_buff.find('</span>', index + len_skip)
            
            str_x_pi = (format_str % input_line_buff[(index + len_skip) : index4])
            line_buff_dst += (str_x_pi)
            input_line_buff = input_line_buff[(index4 + len('</span>')) : ]
            
            # print(str_x_pi)
            
            continue
                    
        # <span class="kuo">
        str_keyword_extend = '<span class=\"kuo\">'
        index1 = input_line_buff.find(str_keyword_extend, index)
        if (index1 == index):
            line_buff_dst += (input_line_buff[: index])
            
            index1 += len(str_keyword_extend)
            index2 = input_line_buff.find('</span>', index1)
            
            str_extend = '[' + (input_line_buff[index1 : index2]) + ']'
            line_buff_dst += str_extend
            
            index2 += len('</span>')
            input_line_buff = input_line_buff[index2 : ]
            
            print(str_extend)
            continue
                        
        # ignore unknown span            
        index = input_line_buff.find('>', index)
        index2 = input_line_buff.find('</span>', index)
        str_unknown_span = input_line_buff[(index + 1) : index2]
        print('warning. unknown span. content: ' + str_unknown_span)
        
        index2 += len('</span>')
        input_line_buff = input_line_buff[index2 : ]
    
    if (len(line_buff_dst) > 0):
        output_buff_array.append(line_buff_dst + '\r\n')
    
def processLine(input_line_buff, output_buff_array):
    if (len(input_line_buff) <= 0):
        return
        
    find_index = input_line_buff.find('<title>', 0)
    if (find_index >= 0):
        find_index += len('<title>')
        find_index2 = input_line_buff.find('</title>', find_index)
        if (find_index2 > find_index):
            str_title = input_line_buff[find_index : find_index2]
            processTitle(output_buff_array, str_title)
        return
        
    find_index = input_line_buff.find('<p', 0)
    if (find_index < 0):
        return
        
    processParagraph(input_line_buff, output_buff_array)    
        
def processFile2(path_i, fileName):
    full_path = os.path.join(path_i, fileName)
    # print(full_path)
    print(fileName)

    global is_normal_chapter
    global chapter_count
    global split_count
    
    tmp_str = ''

    is_normal_chapter = False
            
    outputLineBuff = []
    with open(full_path, 'rt') as file: 
        tmp_str = fileName + ": "
        
        for line_string in file:
            processLine(line_string, outputLineBuff)

    if (len(outputLineBuff) < 1):
        return
        
    if (is_normal_chapter):
        fname = ('chapter_%03d.tex' % (chapter_count - 1))
    else:
        fname = ('split_%03d.tex' % split_count)
        split_count += 1
        
    full_path = os.path.join(path_i, fname)
    
    with open(full_path, 'wt') as file:
        for line_buff in outputLineBuff:
            file.write(line_buff + "\r\n")
    
if __name__ == '__main__':
    # batRename(sys.argv)
    suffixes_filters = []
    
    suffixes_filters.append(".html")
    (list_folders, list_files) = list_folders_files('./text', suffixes_filters)
    print("files: %d" % len(list_files))
    
    for item in sorted(list_files):
        processFile2('./text', item)
