from py2neo import Graph


class Modifier:
    def __init__(self, host="127.0.0.1", post=7474, user=None, password=None, query_dict=None, show_num=10):
        self.g = Graph(host=host,
                       http_post=post,
                       user=user,
                       password=password)
        self.cypher_dict = query_dict
        self.num_limit = show_num

    def _answer_decorator(self, question_type, query_result):
        answer_template = ''
        if question_type == 'movie_actor':
            actors = [obj['a.name'] for obj in query_result]
            title = query_result[0]['m.name']
            answer_template = "《{0}》的主要演员有：{1}".format(title, ','.join(actors[:self.num_limit]))
        elif question_type == 'act_movie':
            titles = [obj['m.name'] for obj in query_result]
            actor = query_result[0]['a.name']
            answer_template = "{0}参演过的电影有：{1}".format(actor, ','.join(titles[:self.num_limit]))
        elif question_type == 'movie_director':
            directors = [obj['d.name'] for obj in query_result]
            title = query_result[0]['m.name']
            answer_template = "《{0}》的导演是：{1}".format(title, ','.join(directors[:self.num_limit]))
        elif question_type == 'direct_movie':
            titles = [obj['m.name'] for obj in query_result]
            director = query_result[0]['d.name']
            answer_template = "{0}导演过的电影有：{1}".format(director, ','.join(titles[:self.num_limit]))
        elif question_type == 'movie_composer':
            composers = [obj['c.name'] for obj in query_result]
            title = query_result[0]['m.name']
            answer_template = "《{0}》的编剧是：{1}".format(title, ','.join(composers[:self.num_limit]))
        elif question_type == 'compose_movie':
            titles = [obj['m.name'] for obj in query_result]
            composer = query_result[0]['c.name']
            answer_template = "{0}制作过的电影有：{1}".format(composer, ','.join(titles[:self.num_limit]))
        elif question_type == 'movie_category':
            answer_template = ''
            for obj in query_result:
                answer = "《{0}》属于{1}类型的电影".format(obj['m.name'], ''.join(obj['m.category']))
                if not answer_template:
                    answer_template += answer
                else:
                    answer_template = answer_template + ';' + answer
        elif question_type == 'movie_showtime':
            answer_template = ''
            for obj in query_result:
                answer = "《{0}》的上映时间是{1}".format(obj['m.name'], obj['m.showtime'])
                if not answer_template:
                    answer_template += answer
                else:
                    answer_template = answer_template + ';' + answer
        elif question_type == 'movie_length':
            answer_template = ''
            for obj in query_result:
                answer = "《{0}》的播放时长是{1}".format(obj['m.name'], obj['m.length'])
                if not answer_template:
                    answer_template += answer
                else:
                    answer_template = answer_template + ';' + answer
        elif question_type == 'movie_othername':
            answer_template = ''
            for obj in query_result:
                answer = "《{0}》的外文名称/别名为：{1}".format(obj['m.name'], '/'.join(obj['m.othername']))
                if not answer_template:
                    answer_template += answer
                else:
                    answer_template = answer_template + ';' + answer
        elif question_type == 'movie_rate':
            answer_template = ''
            for obj in query_result:
                answer = "《{0}》的观影评价为{1},数据来自豆瓣,仅供参考".format(obj['m.name'], str(obj['m.rate']))
                if not answer_template:
                    answer_template += answer
                else:
                    answer_template = answer_template + ';' + answer
        elif question_type == 'movie_desc':
            answer_template = ''
            for obj in query_result:
                answer = "《{0}》的剧情详情请参考链接{1}".format(obj['m.name'], obj['m.url'])
                if not answer_template:
                    answer_template += answer
                else:
                    answer_template = answer_template + ';' + answer
        return answer_template

    def generate_answer(self):
        if self.cypher_dict is None:
            raise ValueError("please input the query_dict value.")
        if isinstance(self.cypher_dict, int) or not self.cypher_dict:
            answer = "主人, 小空还在学习成长, 暂时无法回答你的问题, 抱歉哦"
            return answer
        answers = []
        for question_type, queries in self.cypher_dict.items():
            query_result = []
            for query in queries:
                res = self.g.run(query).data()
                query_result.extend(res)
            query_answer = self._answer_decorator(question_type, query_result)
            answers.append(query_answer)
        return '\n'.join(answers)