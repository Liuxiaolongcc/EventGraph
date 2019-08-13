from sentence_parser import *
import re
from event_graph import *
import jieba.posseg


class TripleExtractor:
    def __init__(self):
        self.parser = LtpParser()

    '''文章分句处理, 切分长句，冒号，分号，感叹号等做切分标识'''

    def split_sents(self, content):
        return [sentence for sentence in re.split(r'[？?！!。；;：:\n\r]', content) if sentence]

    '''利用语义角色标注,直接获取主谓宾三元组,基于A0,A1,A2'''

    def ruler1(self, words, postags, roles_dict, role_index):
        v = words[role_index]
        role_info = roles_dict[role_index]

        if 'A0' in role_info.keys() and 'A1' in role_info.keys():
            s = ''.join([words[word_index] for word_index in range(role_info['A0'][1], role_info['A0'][2]+1) if
                         postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]])
            o = ''.join([words[word_index] for word_index in range(role_info['A1'][1], role_info['A1'][2]+1) if
                         postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]])
            if s and o:
                return '0', [s, v, o]

        # elif 'A1' in role_info.keys() and 'A2' in role_info.keys():
        #     s = ''.join([words[word_index] for word_index in range(role_info['A1'][1], role_info['A1'][2]+1) if
        #                  postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]])
        #     o = ''.join([words[word_index] for word_index in range(role_info['A2'][1], role_info['A2'][2]+1) if
        #                  postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]])
        #     if s and o:
        #         return '1', [s, v, o]

        # elif 'A0' in role_info:
        #     s = ''.join([words[word_index] for word_index in range(role_info['A0'][1], role_info['A0'][2] + 1) if
        #                  postags[word_index][0] not in ['w', 'u', 'x']])
        #     if s:
        #         return '2', [s, v]
        # elif 'A1' in role_info:
        #     o = ''.join([words[word_index] for word_index in range(role_info['A1'][1], role_info['A1'][2]+1) if
        #                  postags[word_index][0] not in ['w', 'u', 'x']])
        #     return '3', [v, o]
        return '4', []

    '''三元组抽取主函数'''

    def ruler2(self, words, postags, child_dict_list, arcs, roles_dict):
        svos = []
        for index in range(len(postags)):
            tmp = 1
            # 先借助语义角色标注的结果，进行三元组抽取
            if index in roles_dict:
                flag, triple = self.ruler1(words, postags, roles_dict, index)
                if flag == '0':
                    triple[1] = self.complete_str(
                        words, index, child_dict_list, 'ADV')
                    svos.append(triple)
                    tmp = 0
            if tmp == 1:
                # 如果语义角色标记为空，则使用依存句法进行抽取
                # if postags[index] == 'v':
                if postags[index]:
                    # 抽取以谓词为中心的事实三元组
                    child_dict = child_dict_list[index]
                    # 主谓宾
                    if 'SBV' in child_dict and 'VOB' in child_dict:
                        r = words[index]
                        r = self.complete_str(
                            words, index, child_dict_list, 'ADV')
                        e1 = self.complete_e(
                            words, postags, child_dict_list, child_dict['SBV'][0])
                        e2 = self.complete_e(
                            words, postags, child_dict_list, child_dict['VOB'][0])
                        svos.append([e1, r, e2])

                    # 定语后置，动宾关系
                    relation = arcs[index][0]
                    head = arcs[index][2]
                    if relation == 'ATT':  # 与父节点是定中关系
                        if 'VOB' in child_dict:  # 与子节点是动宾关系
                            e1 = self.complete_e(
                                words, postags, child_dict_list, head - 1)
                            r = words[index]
                            e2 = self.complete_e(
                                words, postags, child_dict_list, child_dict['VOB'][0])
                            temp_string = r + e2
                            if temp_string == e1[:len(temp_string)]:
                                e1 = e1[len(temp_string):]
                            if temp_string not in e1:
                                svos.append([e1, r, e2])

                    # 含有介宾关系的主谓动补关系
                    if 'SBV' in child_dict and 'CMP' in child_dict:
                        e1 = self.complete_e(
                            words, postags, child_dict_list, child_dict['SBV'][0])
                        cmp_index = child_dict['CMP'][0]
                        r = words[index] + words[cmp_index]
                        if 'POB' in child_dict_list[cmp_index]:
                            e2 = self.complete_e(
                                words, postags, child_dict_list, child_dict_list[cmp_index]['POB'][0])
                            svos.append([e1, r, e2])
        return svos

    '''寻找谓语动词前面的程度副词'''

    # def complete_adv(self, words, index, child_dict_list):
    #     word = words[index]
    #     child_dict = child_dict_list[index]
    #     pre_word = ''
    #     if 'ADV' in child_dict.keys():
    #         ADV_index = child_dict['ADV']
    #         for i in ADV_index:
    #             ee = self.complete_att(words, i, child_dict_list)
    #             pre_word = pre_word + ee
    #         word = pre_word + word
    #         return word
    #     else:
    #         return word
    #
    # def complete_att(self, words, index, child_dict_list):
    #     word = words[index]
    #     child_dict = child_dict_list[index]
    #     pre_word = ''
    #     if 'ATT' in child_dict:
    #         for i in range(len(child_dict['ATT'])):
    #             pre_word += self.complete_att(words,
    #                                           child_dict['ATT'][i], child_dict_list)
    #     return pre_word + word

    def complete_str(self, words, index, child_dict_list, str):
        child_dict = child_dict_list[index]
        pre_word = ''
        if str == 'ADV':
            if 'ADV' in child_dict.keys():
                ADV_index = child_dict['ADV']
                for i in ADV_index:
                    pre_word += self.complete_str(words, i, child_dict_list, 'ATT') + \
                        words[i] + \
                        self.complete_str(words, i, child_dict_list, 'POB')
            return pre_word + words[index]

        elif str == 'ATT':
            if 'ATT' in child_dict.keys():
                for i in range(len(child_dict['ATT'])):
                    pre_word += self.complete_str(
                        words, child_dict['ATT'][i], child_dict_list, 'ATT') + words[child_dict['ATT'][i]]
                return pre_word
            else:
                return ''

        elif str == 'POB':
            if 'POB' in child_dict.keys():
                for i in range(len(child_dict['POB'])):
                    sub = ''.join(words[index+1:child_dict['POB'][i]+1])
                    # for j in range(index+1, child_dict['POB'][i]+1):
                    #     sub += words[j]
                    pre_word = sub + self.complete_str(
                        words, child_dict['POB'][i], child_dict_list, 'POB')
                return pre_word
            else:
                return ''

    '''对找出的主语或者宾语进行扩展'''

    def complete_e(self, words, postags, child_dict_list, word_index):
        child_dict = child_dict_list[word_index]
        prefix = ''
        if 'ATT' in child_dict:
            for i in range(len(child_dict['ATT'])):
                prefix += self.complete_e(words, postags,
                                          child_dict_list, child_dict['ATT'][i])
        postfix = ''
        if postags[word_index] == 'v':
            if 'VOB' in child_dict:
                postfix += self.complete_e(words, postags,
                                           child_dict_list, child_dict['VOB'][0])
            if 'SBV' in child_dict:
                prefix = self.complete_e(
                    words, postags, child_dict_list, child_dict['SBV'][0]) + prefix

        return prefix + words[word_index] + postfix

    def modify(self, svos):
        if len(svos) == 1:
            return svos
        else:
            i = 1
            for item in svos[1:]:
                word_pos = ''
                pos = jieba.posseg.cut(item[0])
                for item in pos:
                    word_pos += str(item)
                if 'r' in word_pos:
                    svos[i][0] = svos[i - 1][2]
                    i += 1
            return svos

    '''程序主控函数'''

    def triples_main(self, content):
        sentences = self.split_sents(content)
        stopwords = ['', ' ', ',', '，', '"', '“', '”']
        svos = []
        for sentence in sentences:
            words, postags, child_dict_list, roles_dict, arcs = self.parser.parser_main(
                sentence)  # arcs是format_parse_list
            svo = self.ruler2(
                words, postags, child_dict_list, arcs, roles_dict)
            svos += [item for item in svo if item[0] not in stopwords and item[1]
                     not in stopwords and item[2] not in stopwords and len(item[2]) <= 15]
            # svos = self.modify(svos)
            # svos += svo

        return svos


'''测试'''
if __name__ == "__main__":
    def hello():
        # with open('./content.txt') as f:
        #     content = f.read()
        content = """中新网8月8日电 据香港《大公报》报道，7日上午，被列为法定古迹的尖沙咀钟楼遭“黑衣男”在墙身喷漆破坏，其间一名正义男途人见到暴徒恶行，挺身而出上前喝止，在遭暴徒打伤下负伤穷追逾1公里，直至暴徒欲登上出租车逃走，出租车司机得悉事件始末后拒绝开车，另一名热心市民亦用身体挡住车门，将其制服
双方追截逾1公里后，暴徒登上一辆出租车，李姓男路人从后面跑来，将出租车截停，并向司机讲出事件始末
该名男路人接受访问时感言：“乱港暴徒作恶多端，我奋不顾身都要将佢(他)绳之于法，以还香港一个安宁
"""
        extractor = TripleExtractor()
        svos = extractor.triples_main(content)
        # with open('./triple.txt', 'w') as f1:
        #     for svo in svos:
        #         f1.write(str(svo))
        #         f1.write('\n')
        print('svos', svos)
    hello()
    # nodes = []
    # edges = []
    # with open('./triple.txt') as f:
    #     for line in f:
    #         triple = line.strip()[1:-1]
    #         triple = triple.split(',')
    #         nodes.append(triple[0])
    #         nodes.append(triple[2])
    #         edges.append(triple)
    #
    # handler = CreatePage()
    # data_nodes, data_edges = handler.collect_data(nodes, edges)
    # handler.create_html(data_nodes, data_edges)
