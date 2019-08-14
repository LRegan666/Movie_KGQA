import os
import json
from py2neo import Graph, Node


DATA_PATH = os.path.abspath('.') + '/data/'


class Movies:
    def __init__(self, path=None):
        self.path = path
        self.data = self.__load_data()

    def __load_data(self):
        with open(self.path, encoding="utf-8") as f:
            data = f.read()
            data_json = json.loads(data)
        return data_json

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.data[key]
        if isinstance(key, slice):
            return self.data[key]
        else:
            raise ValueError("The index value is illegal.")


class MovieGraph:
    def __init__(self, data=None, graph_host='127.0.0.1', graph_post=7474,
                 graph_user=None, graph_password=None):
        self.data = data
        self.g = Graph(host=graph_host,
                       http_post=graph_post,
                       user=graph_user,
                       password=graph_password)
        self.movie_desc_keys = ['title', 'url', 'rate', 'category',
                                'showtime', 'length', 'othername']
        self.movie_titles, self.directors, self.composers, self.actors = [], [], [], []

    def __store_entities(self):
        for name, data in zip(('movie.txt', 'director.txt', 'composer.txt', 'actor.txt'),
                              (self.movie_titles, self.directors, self.composers, self.actors)):
            with open(DATA_PATH+name, 'w+') as f:
                f.write('\n'.join(data))
        return

    def _entity_collector(self):
        if not self.data:
            raise ValueError("Please the effective data.")
        relation_director, relation_composer, relation_actor, movie_infos = [], [], [], []
        movie_desc = {}
        for movie in self.data:
            if 'title' in movie:
                self.movie_titles.append(movie['title'])
            if 'director' in movie and isinstance(movie['director'], list) \
                    and len(movie['director']) > 0:
                self.directors.extend(movie['director'])
                relation_director.extend(list(zip([movie['title']]*len(movie['director']), movie['director'])))
            if 'composer' in movie and isinstance(movie['composer'], list) \
                    and len(movie['composer']) > 0:
                self.composers.extend(movie['composer'])
                relation_composer.extend(list(zip([movie['title']]*len(movie['composer']), movie['composer'])))
            if 'actor' in movie and isinstance(movie['actor'], list) \
                    and len(movie['actor']) > 0:
                self.actors.extend(movie['actor'])
                relation_actor.extend(list(zip([movie['title']]*len(movie['actor']), movie['actor'])))
            for key in self.movie_desc_keys:
                if key in movie:
                    movie_desc[key] = movie[key]
            if movie_desc not in movie_infos:
                movie_infos.append(movie_desc)
            movie_desc = {}
        self.movie_titles = list(set(self.movie_titles))
        self.directors = list(set(self.directors))
        self.composers = list(set(self.composers))
        self.actors = list(set(self.actors))
        self.__store_entities()
        return self.directors, self.composers, self.actors, movie_infos, \
               relation_director, relation_composer, relation_actor

    def _create_graph_nodes(self, entity_infos):
        directors, composers, actors, movie_infos, _, _, _ = entity_infos
        for movie_desc in movie_infos:
            node = Node('Movie',
                        name=movie_desc['title'],
                        url=movie_desc['url'],
                        rate=movie_desc['rate'],
                        category=movie_desc['category'],
                        showtime=movie_desc['showtime'],
                        length=movie_desc['length'],
                        othername=movie_desc['othername'])
            self.g.create(node)
        for entities in zip(('Director', 'Composer', 'Actor'), (directors, composers, actors)):
            for entity in entities[1]:
                node = Node(entities[0], name=entity)
                self.g.create(node)
        print("+ It's completed to create the entity node in the graph.")

    def _create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        edges_filter = ['<>'.join(edge) for edge in edges]
        edges_filter = list(set(edges_filter))
        for edge in edges_filter:
            s, e = edge.split('<>')
            cypher = 'match (p:%s),(q:%s) where p.name="%s" ' \
                     'and q.name="%s" create (p)-[rel:%s{name:"%s"}]->(q)' % (start_node, end_node,
                                                                              s, e, rel_type, rel_name)
            try:
                self.g.run(cypher)
            except Exception as e:
                print("Create Relation Error: %s" % str(e))
        print("++ It's completed to create the %s-%s relation in the graph." % (start_node, end_node))

    def _create_graph_relations(self, entity_infos):
        _, _, _, _, relation_director, relation_composer, relation_actor = entity_infos
        self._create_relationship('Movie', 'Director', relation_director, 'lead', '主导')
        self._create_relationship('Movie', 'Composer', relation_composer, 'create', '创作')
        self._create_relationship('Movie', 'Actor', relation_actor, 'participate', '参与')

    def build_Graph(self):
        entity_infos = self._entity_collector()
        self._create_graph_nodes(entity_infos)
        self._create_graph_relations(entity_infos)
        print("+++ It's completed to build the movie graph.")


if __name__ == '__main__':
    data_path = os.path.abspath('.') + '/data/dbmovies.json'
    m = Movies(path=data_path)
    print(m[600])
    print(len(m[600]))