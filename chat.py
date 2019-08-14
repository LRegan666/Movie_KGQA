import os
from data_utils import Movies, MovieGraph, DATA_PATH
from question_analysis_tools import question_parser, answer_assembler


class QABot:
    def __init__(self, data_path=None, host=None, post=None, user=None, password=None, start_up=True):
        self.host, self.post, self.user, self.password = host, post, user, password
        self.graph = MovieGraph(data=Movies(path=data_path),
                                graph_host=self.host,
                                graph_post=self.post,
                                graph_user=self.user,
                                graph_password=self.password)
        self.parser = question_parser
        self.assembler = answer_assembler
        if start_up:
            self.graph.build_Graph()
            self.entities = (self.graph.movie_titles, self.graph.directors,
                             self.graph.composers, self.graph.actors)
        else:
            self.entities = self.__load_entities()

    def __load_entities(self):
        entities = dict()
        for entity_name in ('movie', 'director', 'composer', 'actor'):
            entities[entity_name] = []
            with open(DATA_PATH+entity_name+'.txt', 'r') as f:
                for line in f.readlines():
                    line = line.strip('\n')
                    entities[entity_name].append(line)
        return entities['movie'], entities['director'], entities['composer'], entities['actor']

    def session(self, question):
        extractor = self.parser.Extractor(entities=self.entities, sentence=question)
        cypher_queries = extractor.cypher_collector()
        modifier = self.assembler.Modifier(host=self.host,
                                           post=self.post,
                                           user=self.user,
                                           password=self.password,
                                           query_dict=cypher_queries)
        answer = modifier.generate_answer()
        return answer


if __name__ == '__main__':
    path = os.path.abspath('.') + '/data/dbmovies.json'
    bot = QABot(data_path=path,
                host='127.0.0.1',
                post=7474,
                user='neo4j',
                password='123456',
                start_up=False)
    cur_num, pre_num = 0, 0
    start_signal = True
    while 1:
        if start_signal:
            print("小空：您好,主人.我是电影问答助理小空,请问有什么可以帮您")
            start_signal = False
        question = input("主人：")
        answer = bot.session(question)
        if '小空' in answer:
            cur_num += 1
        if cur_num > 2:
            print("小空：主人频繁问一些奇怪的问题,小空已经不知所错了,请及时修正")
            pre_num = cur_num = 0
            continue
        print("小空：", answer)
        if cur_num == pre_num and cur_num != 0:
            pre_num = cur_num = 0
        if cur_num != pre_num:
            pre_num = cur_num
