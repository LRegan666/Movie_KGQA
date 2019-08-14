import ahocorasick


class Extractor:
    def __init__(self, entities=None, sentence=None):
        self.cate_entities = entities
        self.sentence = sentence
        self.entity_list = None
        self.entity_actree = self.__build_actree()
        self.entity_dict = self.__build_entity_dict()
        self.act_rels = ['演员', '主演', '参演', '表演', '演出', '演了']
        self.direct_rels = ['导演', '导过', '导了', '主导']
        self.compose_rels = ['编剧', '制作', '编制', '编写', '创作']
        self.category_rels = ['类型', '类别', '风格', '种类', '品类']
        self.showtime_rels = ['啥时间', '什么时间', '上映时间', '播放时间', '播出时间',
                              '具体时间', '啥时候', '什么时候', '年', '年份', '日期', '上映']
        self.length_rels = ['时长', '多长', '多久', '长度']
        self.othername_rels = ['别名', '名称', '名字']
        self.rate_rels = ['评分', '口碑', '评级', '分数', '评价', '质量', '值得', '怎么样', '咋样']
        self.desc_rels = ['故事', '内容', '讲了', '描述', '讲述', '介绍', '简介']

    def __build_actree(self):
        if not self.cate_entities:
            raise ValueError("entities parameter type is wrong.")
        entity_list = []
        for entities in self.cate_entities:
            entity_list.extend(entities)
        self.entity_list = list(set(entity_list))
        actree = ahocorasick.Automaton()
        for ind, entity in enumerate(self.entity_list):
            actree.add_word(entity, (ind, entity))
        actree.make_automaton()
        return actree

    def __build_entity_dict(self):
        entity_dict = {}
        for entity in self.entity_list:
            entity_dict[entity] = []
            for category, cate_entity_list in zip(('movie', 'director', 'composer', 'actor'), self.cate_entities):
                if entity in cate_entity_list:
                    entity_dict[entity].append(category)
        return entity_dict

    def __sentence_filter(self, sentence):
        effective_words = []
        for ret in self.entity_actree.iter(sentence):
            word = ret[1][1]
            effective_words.append(word)
        words_list_length = len(effective_words)
        stop_words = []
        for i in range(words_list_length):
            for j in range(i + 1, words_list_length):
                if effective_words[i] != effective_words[j]:
                    if effective_words[i] in effective_words[j]:
                        stop_words.append(effective_words[i])
                    elif effective_words[j] in effective_words[i]:
                        stop_words.append(effective_words[j])
        stop_words = list(set(stop_words))
        word_dict = {}
        for word in effective_words:
            if word not in stop_words:
                word_dict[word] = self.entity_dict[word]
        return word_dict

    def __question_type_check(self, key_words, sentence):
        for word in key_words:
            if word in sentence:
                return True
        return False

    def _category_extraction(self):
        if not isinstance(self.sentence, str) or not self.sentence:
            raise ValueError("The sentence value type is illegal.")
        cate_dict = {}
        cate_dict['args'] = self.__sentence_filter(self.sentence)
        word_types = []
        for word_type in cate_dict['args'].values():
            word_types.extend(word_type)
        word_types = list(set(word_types))
        cate_dict['question_type'] = []
        if self.__question_type_check(self.act_rels, self.sentence):
            if 'movie' in word_types:
                sentence_category = 'movie_actor'
                cate_dict['question_type'].append(sentence_category)
            if 'actor' in word_types:
                sentence_category = 'act_movie'
                cate_dict['question_type'].append(sentence_category)
        if self.__question_type_check(self.direct_rels, self.sentence):
            if 'movie' in word_types:
                sentence_category = 'movie_director'
                cate_dict['question_type'].append(sentence_category)
            if 'director' in word_types:
                sentence_category = 'direct_movie'
                cate_dict['question_type'].append(sentence_category)
        if self.__question_type_check(self.compose_rels, self.sentence):
            if 'movie' in word_types:
                sentence_category = 'movie_composer'
                cate_dict['question_type'].append(sentence_category)
            if 'composer' in word_types:
                sentence_category = 'compose_movie'
                cate_dict['question_type'].append(sentence_category)
        if self.__question_type_check(self.category_rels, self.sentence) and 'movie' in word_types:
            sentence_category = 'movie_category'
            cate_dict['question_type'].append(sentence_category)
        if self.__question_type_check(self.showtime_rels, self.sentence) and 'movie' in word_types:
            sentence_category = 'movie_showtime'
            cate_dict['question_type'].append(sentence_category)
        if self.__question_type_check(self.length_rels, self.sentence) and 'movie' in word_types:
            sentence_category = 'movie_length'
            cate_dict['question_type'].append(sentence_category)
        if self.__question_type_check(self.othername_rels, self.sentence) and 'movie' in word_types:
            sentence_category = 'movie_othername'
            cate_dict['question_type'].append(sentence_category)
        if self.__question_type_check(self.rate_rels, self.sentence) and 'movie' in word_types:
            sentence_category = 'movie_rate'
            cate_dict['question_type'].append(sentence_category)
        if self.__question_type_check(self.desc_rels, self.sentence) and 'movie' in word_types:
            sentence_category = 'movie_desc'
            cate_dict['question_type'].append(sentence_category)
        return cate_dict

    def __cypher_transfer(self, question_type, entity_list):
        cypher_queries = []
        if question_type == 'movie_actor':
            cypher_queries = ["match (m:Movie)-[r:participate]->(a:Actor) " \
                              "where m.name='{0}' return m.name, a.name".format(entity) for entity in entity_list]
        elif question_type == 'act_movie':
            cypher_queries = ["match (m:Movie)-[r:participate]->(a:Actor) " \
                              "where a.name='{0}' return m.name, a.name".format(entity) for entity in entity_list]
        elif question_type == 'movie_director':
            cypher_queries = ["match (m:Movie)-[r:lead]->(d:Director) " \
                              "where m.name='{0}' return m.name, d.name".format(entity) for entity in entity_list]
        elif question_type == 'direct_movie':
            cypher_queries = ["match (m:Movie)-[r:lead]->(d:Director) " \
                              "where d.name='{0}' return m.name, d.name".format(entity) for entity in entity_list]
        elif question_type == 'movie_composer':
            cypher_queries = ["match (m:Movie)-[r:create]->(c:Composer) " \
                              "where m.name='{0}' return m.name, c.name".format(entity) for entity in entity_list]
        elif question_type == 'compose_movie':
            cypher_queries = ["match (m:Movie)-[r:create]->(c:Composer) " \
                              "where c.name='{0}' return m.name, c.name".format(entity) for entity in entity_list]
        elif question_type == 'movie_category':
            cypher_queries = ["match (m:Movie) where m.name='{0}' " \
                              "return m.name, m.category".format(entity) for entity in entity_list]
        elif question_type == 'movie_showtime':
            cypher_queries = ["match (m:Movie) where m.name='{0}' " \
                              "return m.name, m.showtime".format(entity) for entity in entity_list]
        elif question_type == 'movie_length':
            cypher_queries = ["match (m:Movie) where m.name='{0}' " \
                              "return m.name, m.length".format(entity) for entity in entity_list]
        elif question_type == 'movie_othername':
            cypher_queries = ["match (m:Movie) where m.name='{0}' " \
                              "return m.name, m.othername".format(entity) for entity in entity_list]
        elif question_type == 'movie_rate':
            cypher_queries = ["match (m:Movie) where m.name='{0}' " \
                              "return m.name, m.rate".format(entity) for entity in entity_list]
        elif question_type == 'movie_desc':
            cypher_queries = ["match (m:Movie) where m.name='{0}' " \
                              "return m.name, m.url".format(entity) for entity in entity_list]
        return cypher_queries

    def _generate_cypher(self, category_dict):
        if not category_dict['args']:
            return -1
        cate2ent = dict()
        for entity in category_dict['args']:
            for cate in self.entity_dict[entity]:
                if cate not in cate2ent:
                    cate2ent[cate] = [entity]
                elif entity not in cate2ent[cate]:
                    cate2ent[cate].append(entity)
        cypher_queries, queries = {}, []
        type_tuples = ('movie_actor', 'movie_director', 'movie_composer', 'movie_category',
                       'movie_showtime', 'movie_length', 'movie_othername', 'movie_rate', 'movie_desc')
        for question_type in category_dict['question_type']:
            if question_type in type_tuples:
                queries = self.__cypher_transfer(question_type, cate2ent['movie'])
            elif question_type == 'act_movie':
                queries = self.__cypher_transfer(question_type, cate2ent['actor'])
            elif question_type == 'direct_movie':
                queries = self.__cypher_transfer(question_type, cate2ent['director'])
            elif question_type == 'compose_movie':
                queries = self.__cypher_transfer(question_type, cate2ent['composer'])
            if queries:
                if question_type not in cypher_queries:
                    cypher_queries[question_type] = queries
                else:
                    cypher_queries[question_type].extend(queries)
        return cypher_queries

    def cypher_collector(self):
        cate_dict = self._category_extraction()
        cql_infos = self._generate_cypher(cate_dict)
        return cql_infos
