from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import PCA
from plotnine import *
import pandas as pd
from sklearn.base import clone
from sklearn.preprocessing import OneHotEncoder


RANDOM_STATE = 314

class Clustering(object):
    #TODO: make safer w a primary key
    def __init__(self, X):
        """
        :param X: pandas dataframe or all features to be clustered on
        """
        self.X = X

    def elbow(self, model, wcss_func, max_n_clusters=12):
        """
        :param model: ex KMeans (before function called)
        :param wcss_func: (model, X, n_clusters) -> wcss
            model: ex KMeans (before function called)
        :param max_n_clusters:  int
        :return: None
        """
        wcss = []
        for i in range(1, max_n_clusters):
            wcss.append(wcss_func(model, self.X, i))

        elbow_df = pd.DataFrame({"n_clusters":range(1, max_n_clusters),
                                 "wcss": wcss})

        self.elbow_plot = ggplot(elbow_df, aes("n_clusters", wcss)) +\
            geom_point() +\
            geom_line()

        print(self.elbow_plot)

    def train_model_and_one_hot_training_data(self, model):
        """
        :param model: after function called (ex Kmeans(n_clusters=4))
        :return: None
        """
        self.model = model.fit(self.X)
        self.train_clusters = pd.DataFrame(
            {"train_row": range(self.X.shape[0]),
             "cluster": self.model.predict(self.X)})
        self.train_cluster_count_plot = ggplot(self.train_clusters, aes("cluster")) +\
            geom_bar()
        print(self.train_cluster_count_plot)
        self.one_hot_clusterer = OneHotEncoder()
        self.one_hotted_train_data = pd.DataFrame(
            self.one_hot_clusterer.fit_transform(self.train_clusters[["cluster"]]).toarray())
        assert self.X.shape[0] == self.one_hotted_train_data.shape[0], "shape if off"
        self.X_w_one_hots = self.X.join(self.one_hotted_train_data)

    def predict_new_clusters(self, new_X):
        """
        Important to have for testing data
        :param model: after function called (ex Kmeans(n_clusters=4))
        :return: (clusters, onehotted
        """
        if self.model is None:
            print("you need to train 1st")
        else:
            new_clusters = self.model.predict(new_X)
            new_onehots = self.one_hot_clusterer.transform(new_clusters.reshape(-1,1))
            return new_clusters, new_onehots

    def view_2d_pca_projection_of_training_data(self, n_components="ncols"):
        if n_components == "ncols":
            n_components = self.X.shape[1]
        self.pca = PCA(n_components=n_components)
        self.pcs = self.pca.fit_transform(self.X)
        print(f"explained variance ratio: {self.pca.explained_variance_ratio_}")
        pc_df = pd.DataFrame(
            {"pc1": self.pcs[:,0],
             "pc2": self.pcs[:,1]}
        ).assign(cluster=self.train_clusters["cluster"].astype(str))
        p = ggplot(pc_df, aes("pc1", "pc2", fill="cluster")) +\
            geom_point()
        print(p)

    def check_model_assumptions(self):
        """
        implement!
        for all children of this class
        :return:
        """
        pass






def kmeans_wcss(model, X, n_clusters):
    """
    references: https://medium.com/@iSunilSV/data-science-python-k-means-clustering-eed68b490e02
    :param model: pre function call
    :param X:
    :param n_clusters: int
    :return: float wcss
    """
    kmeans = model(n_clusters=n_clusters, random_state=RANDOM_STATE)
    kmeans.fit(X)
    return kmeans.inertia_



class KmeansClustering(Clustering):

    def __init__(self, X):
        Clustering.__init__(self, X)

    def elbow(self, max_n_clusters=12):
        Clustering.elbow(self, KMeans, kmeans_wcss, 12)

    def train_model_and_one_hot_training_data(self, num_clusters):
        kmeans = KMeans(n_clusters=num_clusters,
                            init= 'k-means++', # smart way of selecting initial clusters to speed up the process
                            max_iter = 300,
                            n_init = 10, # num centroid seeds
                            random_state = RANDOM_STATE)
        Clustering.train_model_and_one_hot_training_data(self, kmeans)

    def check_variance_per_assigned_cluster(self):
        print("\n\n\nhere are the variances per assigned cluster")
        X_w_clusters = self.X.copy()
#         import ipdb; ipdb.set_trace()
        X_w_clusters["cluster"] = self.train_clusters["cluster"]
        for clust in self.train_clusters['cluster'].unique():
            this_clust_df = X_w_clusters[X_w_clusters.cluster == clust]
            clust_variance = this_clust_df.iloc[:, :-1].var(axis=0)
            print(f"cluster: {clust} \ncluster variance: \n{clust_variance}")

    def check_cluster_sizes_vs_hclust(self):
        print(f"here is the cluster sizes we're guessing w kmeans: {self.train_cluster_count_plot}")
        hclust = AgglomerativeClustering(n_clusters=len(self.train_clusters["cluster"].unique()))
        hclust.fit(self.X)
        hclust_clusters = pd.DataFrame(
            {"train_row": range(self.X.shape[0]),
             "cluster": hclust.predict(self.X)})
        hclust_cluster_count_plot = ggplot(hclust_clusters, aes("cluster")) + \
                                        geom_bar()
        print(hclust_cluster_count_plot)




    def check_model_assumptions(self):
        """
        resources: http://varianceexplained.org/r/kmeans-free-lunch/
        :return:
        """
        if self.model is None:
            print("train model 1st")
        else:
            self.check_variance_per_assigned_cluster()
            self.view_2d_pca_projection_of_training_data()
#             self.check_cluster_sizes_vs_hclust() # little slow, can probably tune to speed it up
