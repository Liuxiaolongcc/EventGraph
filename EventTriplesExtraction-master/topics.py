# coding=utf-8
'''提取文本的摘要'''
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import codecs
from triple_extraction import*

class summarize():
    def __init__(self):
        self.extractor = extractor = TripleExtractor()
        self.tr4s = TextRank4Sentence()

    def Prune(self, triples):
        update_triple = [triples[0]]
        for i in range(len(triples)):
            if triples[i] == update_triple[-1]:
                continue
            if ''.join(triples[i]) == update_triple[-1][-1]:

                continue
            update_triple.append(triples[i])
        return update_triple

    def summary_main(self, text):
        self.tr4s.analyze(text=text, lower=True, source='all_filters')
        content = ''
        #可在此通过修改num的值来改变摘要的数量
        for item in self.tr4s.get_key_sentences(num=10):
            content += item.sentence + '\n'
        #对提取出来的摘要再进行事件抽取
        svos, r_ps, svos_pre = self.extractor.triples_main(content)
        update_triple = self.Prune(svos_pre)
        return update_triple

if __name__ == "__main__":
    text = codecs.open('./content.txt', 'r', 'utf-8').read()
    summarizor = summarize()
    triples = summarizor.summary_main(text)
    with open('./summary.txt', 'w') as f:
        for item in triples:
            f.write(''.join(item) + '\n')
