import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import Reader, Dataset, SVD

class hybridRecommender:
    def __init__(self) -> None:
        pass

    def load_dataset(self, reduced = False):
        if reduced == False:
            self.df = pd.read_csv('./archive/movies_metadata.csv', low_memory=False)
        else:
            whole_df = pd.read_csv('./archive/movies_metadata.csv', low_memory=False)
            whole_df = whole_df.drop([19730, 29503, 35587])
            whole_df['id'] = whole_df['id'].astype('int')
            links_small = pd.read_csv('./archive/links_small.csv')
            links_small = links_small[links_small['tmdbId'].notnull()]['tmdbId'].astype('int')
            self.df = whole_df[whole_df['id'].isin(links_small)]
            self.df.to_csv("./archive/reduced_movie_metadata.csv")
            del whole_df
            del links_small

    def calculate_cosine_sim(self):
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.df['overview'] = self.df['overview'].fillna('')
        self.tfidf_matrix = self.tfidf.fit_transform(self.df['overview'])
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)

    def content_based_recommender(self, title, cosine_sim = None):
        if cosine_sim == None:
            cosine_sim = self.cosine_sim
        indices = pd.Series(self.df.index, index=self.df['title'])
        indices = indices[~indices.index.duplicated(keep='last')]
        movie_index = indices[title]
        similarity_scores = pd.self.df(cosine_sim[movie_index], columns=["score"])
        movie_indices = similarity_scores.sort_values("score", ascending=False)[1:11].index
        return self.df['title'].iloc[movie_indices]
    
    def recommend(self):
        recommendations = np.empty(self.df.shape[0]*11, dtype = np.object).reshape(self.df.shape[0], 11)
        j = 0
        for i in self.df['title']:
            recommendations[j][0] = i
            recommendations[j][1:] = self.content_based_recommender(i).to_numpy()
            j = j + 1
        return recommendations

    def reduce_memory_usage(self, verbose=True):
        numerics = ["int8", "int16", "int32", "int64", "float16", "float32", "float64"]
        start_mem = self.df.memory_usage().sum() / 1024 ** 2
        for col in self.df.columns:
            col_type = self.df[col].dtypes
            if col_type in numerics:
                c_min = self.df[col].min()
                c_max = self.df[col].max()
                if str(col_type)[:3] == "int":
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        self.df[col] = self.df[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        self.df[col] = self.df[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        self.df[col] = self.df[col].astype(np.int32)
                    elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                        self.df[col] = self.df[col].astype(np.int64)
                else:
                    if (
                        c_min > np.finfo(np.float16).min
                        and c_max < np.finfo(np.float16).max
                    ):
                        self.df[col] = self.df[col].astype(np.float16)
                    elif (
                        c_min > np.finfo(np.float32).min
                        and c_max < np.finfo(np.float32).max
                    ):
                        self.df[col] = self.df[col].astype(np.float32)
                    else:
                        self.df[col] = self.df[col].astype(np.float64)
        end_mem = self.df.memory_usage().sum() / 1024 ** 2
        if verbose:
            print(
                "Mem. usage decreased to {:.2f} Mb ({:.1f}% reduction)".format(
                    end_mem, 100 * (start_mem - end_mem) / start_mem
                )
            )
        return self.df
    
class tfidRecommender:
    def __init__(self) -> None:
        pass

    def load_dataset(self, reduced = False):
        if reduced == False:
            self.df = pd.read_csv('./archive/movies_metadata.csv', low_memory=False)
        else:
            self.df = pd.read_csv('./archive/reduced_movie_metadata.csv', low_memory=False)

    def calculate_cosine_sim(self):
        self.tfidf = TfidfVectorizer(stop_words='english')
        print("Checkpoint 1: TfidVecorizer completion")
        self.df['overview'] = self.df['overview'].fillna('')
        self.tfidf_matrix = self.tfidf.fit_transform(self.df['overview'])
        print("Checkpoint 2: Fitting and Transform completion")
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        print("Checkpoint 3: Similarity completion")
        print(self.cosine_sim)

    def content_based_recommender(self, title, cosine_sim = None):
        if cosine_sim == None:
            cosine_sim = self.cosine_sim

        similarity_scores = pd.DataFrame(cosine_sim[self.df[self.df['title'] == title].iloc[0, 0]], columns=["score"])
        movie_indices = similarity_scores.sort_values("score", ascending=False)[1:11].index
        return self.df['title'].iloc[movie_indices]
    
    def recommend(self):
        recommendations = np.zeros(self.df.shape[0]*11, dtype = object).reshape(self.df.shape[0], 11)
        j = 0
        for i in self.df['title']:
            # print(j)
            recommendations[j][0] = i
            recommendations[j][1:] = (self.content_based_recommender(i)).to_numpy()
            j = j + 1
        return recommendations

    def reduce_memory_usage(self, verbose=True):
        numerics = ["int8", "int16", "int32", "int64", "float16", "float32", "float64"]
        start_mem = self.df.memory_usage().sum() / 1024 ** 2
        for col in self.df.columns:
            col_type = self.df[col].dtypes
            if col_type in numerics:
                c_min = self.df[col].min()
                c_max = self.df[col].max()
                if str(col_type)[:3] == "int":
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        self.df[col] = self.df[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        self.df[col] = self.df[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        self.df[col] = self.df[col].astype(np.int32)
                    elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                        self.df[col] = self.df[col].astype(np.int64)
                else:
                    if (
                        c_min > np.finfo(np.float16).min
                        and c_max < np.finfo(np.float16).max
                    ):
                        self.df[col] = self.df[col].astype(np.float16)
                    elif (
                        c_min > np.finfo(np.float32).min
                        and c_max < np.finfo(np.float32).max
                    ):
                        self.df[col] = self.df[col].astype(np.float32)
                    else:
                        self.df[col] = self.df[col].astype(np.float64)
        end_mem = self.df.memory_usage().sum() / 1024 ** 2
        if verbose:
            print(
                "Mem. usage decreased to {:.2f} Mb ({:.1f}% reduction)".format(
                    end_mem, 100 * (start_mem - end_mem) / start_mem
                )
            )
        return self.df

if __name__ == '__main__':
    print("This is a Recommender model")

    model_rec = tfidRecommender() 

    def train_model(model_name):
        model_name.load_dataset(reduced = True)
        model_name.reduce_memory_usage()
        model_name.calculate_cosine_sim()
        return model_name.recommend()
    
    model_v1 = train_model(model_rec)
    mod={}
    for i in model_v1:
        mod[i[0]]=i[1:].tolist()

    import pickle
    with open("rec_model", "wb") as file:
        pickle.dump(mod, file)
    del model_rec
    del model_v1