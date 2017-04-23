import numpy as np
from numpy.linalg import inv
import pandas as pd
from sklearn.metrics import mean_squared_error


def get_mse(pred, actual):
    # Ignore nonzero terms.
    pred = pred[actual.nonzero()].flatten()

    actual = actual[actual.nonzero()].flatten()
    return mean_squared_error(pred, actual)

def train_test_split(ratings):
    test = np.zeros(ratings.shape)
    train = ratings.copy()
    for user in xrange(ratings.shape[0]):
        test_ratings = np.random.choice(ratings[user, :].nonzero()[0],
                                        size=10,
                                        replace=False)

        train[user, test_ratings] = 0.
        test[user, test_ratings] = ratings[user, test_ratings]

    return train, test

def predict(u, i):
    global user_matrix
    global movie_matrix
    return user_matrix[u, :].dot(movie_matrix[i, :].T)

def als_user(movie_mat, user_mat, ratings):
    global reg_user
    global num_users

    YTY = movie_mat.T.dot(movie_mat)
    const_user = np.eye(YTY.shape[0]) * reg_user
    for u in range(num_users):
        user_mat[u, :] = ratings[u, :].dot(movie_mat).dot(inv(YTY + const_user))

    return user_mat


def als_movie(movie_mat, user_mat, ratings):
    global reg_movies
    global num_movies

    XTX = user_mat.T.dot(user_mat)
    const_movies = np.eye(XTX.shape[0]) * reg_movies
    for i in range(num_movies):
        movie_mat[i, :] = ratings[:, i].T.dot(user_mat).dot(inv(XTX + const_movies))

    return movie_mat

''' Number of latent factors'''

reg_user = 0.1
reg_movies = 0.1

#df = pd.read_csv('u.data', sep='\t', names=cols)
df = pd.read_csv('ratings_processed.csv')
#del df['time']

user_list = df['user_id'].drop_duplicates().tolist()
user_list.sort()

movie_list = df['movie_id'].drop_duplicates().tolist()
movie_list.sort()

num_users = len(user_list)
num_movies = len(movie_list)

'''Creating a rating matrix'''
ratings = np.zeros((num_users, num_movies))
for index, row in df.iterrows():
    ratings[int(row['user_id']), int(row['movie_id'])] = row['rating']

itern_list = [ 100]
k_list = [ 30]
#lambda_list = np.logspace(-3, 2.0, num=2)
lambda_list = [0.1]

data = []
for lambda_ in lambda_list:
    #row = []
    reg_user = lambda_
    reg_movies = lambda_
    print " --------- lambda = " + str(lambda_) + "-------------"
    train, test = train_test_split(ratings=ratings)
    #row.append(lambda_)
    for k in k_list:
        print "k = " + str(k)
        #row.append(k)
        for iter_cur in itern_list:
            print "Iterations = " + str(iter_cur)
            #row.append(iter_cur)
            user_matrix = np.random.random((num_users, k))
            movie_matrix = np.random.random((num_movies, k))
            for j in range(iter_cur):
                movie_matrix = als_movie(movie_mat=movie_matrix, user_mat=user_matrix, ratings=train)
                user_matrix = als_user(movie_mat=movie_matrix, user_mat=user_matrix, ratings=train)

            predictions = np.zeros((num_users, num_movies))
            for u in xrange(num_users):
                for i in xrange(num_movies):
                    predictions[u, i] = predict(u, i)

            pred_max, pred_min = predictions.max(), predictions.min()
            predictions = (predictions - pred_min) / (pred_max - pred_min)

            for u in xrange(num_users):
                for i in xrange(num_movies):
                    predictions[u, i] = round(predictions[u, i] * 5, 0)

            #print predictions[12][32]
            #row.append(get_mse(predictions, train))
            #row.append(get_mse(predictions, test))
            test_ms = get_mse(predictions, test)
            data.append(test_ms)
            print "Training MSE: "+str(get_mse(predictions, train)) + " Test MSE: " + str(test_ms)

print min(data)
