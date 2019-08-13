# EventGraph
事件抽取及可视化程序使用说明

一.需要安装的库
os, pyltp, jieba, re, textrank4zh, codecs;

二.各模块功能说明
1,sentence_parser.py主要用来解析句子的语法结构;
2,content.txt为需要分析的文本, triple.txt为基于文本提取出来的事件三元组, r_ps.txt为三元组中第二个元素的属性, summary.txt存储文本的摘要;
3,triple_extraction.py用来提取content.txt中文本的事件,以三元组形式表示,形成事件图谱;
4,event_graph.py用来可视化提取出来的事件图谱;
5,topics.py用来提取文本中的摘要

三.使用步骤及图示
1,将要分析的文本写入文件:content.txt;
2,运行主程序:triple_extraction.py;
3,浏览器打开event_graph.html文件查看对应的可视化事件图谱;打开triple.txt和r_ps.txt分别可以查看抽取出来的三元组及三元组中第二元素的属性;
4,运行topics.py可以在summay.txt中查看文本的摘要
