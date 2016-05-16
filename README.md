# WebSearchEngine-API

Implementation of different techniques used in Web Search Engine.

Classification techiniques:

<b>1. Naive Bayes</b>

![equation](https://latex.codecogs.com/gif.latex?P%28c_i%7C%5Coverrightarrow%7Bd_j%7D%29%20%3D%20%5Cfrac%7BP%28%5Coverrightarrow%7Bd_j%7D%7Cc_i%29%20.%20p%28c_i%29%7D%7BP%28%5Coverrightarrow%7Bd_j%7D%29%7D)

The key is how to compute the posterior probability ![equation](https://latex.codecogs.com/gif.latex?P%28c_i%7C%5Coverrightarrow%7Bd_j%7D%29) that document d<sub>j</sub> belongs to category c<sub>i</sub>. According to Bayes formula, the posterior probability ![equation](https://latex.codecogs.com/gif.latex?P%28c_i%7C%5Coverrightarrow%7Bd_j%7D%29) is translated to compute the prior probability ![equation](https://latex.codecogs.com/gif.latex?P%28%5Coverrightarrow%7Bd_j%7D%7Cc_i%29). Then, the categories that have the most prior probability are judged into the final categories of document d<sub>j</sub>.

Here P(c<sub>i</sub>) denotes the probability of category csub>i</sub> in the training set and P(dsub>j</sub>) denotes document dsub>j</sub> in the training set. Because P(dsub>j</sub>) is invariant for a given document dsub>j</sub> in all categories. The final category is decided by following formula :


![equation](https://latex.codecogs.com/gif.latex?argmax_%7Bc_i%7D%20P%28c_i%7Cd_j%29%20%3D%20argmax_%7Bc_i%7D%20P%28%5Coverrightarrow%7Bd_j%7D%7Cc_i%29%20.%20P%28c_i%29)


We have used Multinomial Naive Bayes, in which we take into account the term frequency in the class, the term count of the class and vocabulary of the dataset. If   ![equation](https://latex.codecogs.com/gif.latex?%5Coverrightarrow%7Bd_j%7D%20%3D%20%28%7Bw_1%2Cw_2........w_n%7D%29), then the probability of a token wsub>j</sub> given class c<sub>i</sub> is calculated by


![equation](https://latex.codecogs.com/gif.latex?P%28%5Coverrightarrow%7Bw_j%7D%7Cc_i%29%20%3D%20%5Cfrac%7Bcount%28w_j%2Cc_i%29%20&plus;%201%7D%7Bcount%28c%29%20&plus;%20%7CV%7C%7D)

Using this, the probability of a document given the class is given by


![equation](https://latex.codecogs.com/gif.latex?P%28%5Coverrightarrow%7Bd_j%7D%7Cc_i%29%20%3D%20P%28c_i%29%20.%20P%28w_1%7Cc_i%29%20.%20P%28w_2%7Cc_i%29.......P%28w_n%7Cc_i%29)

<b>2. K-means Clustering</b>

<i>Algorithm Pseudocode</i>:
   - Pick K mean vectors using labeled data
   - Calculate initial mean and allow documents to assign to different cluster contradicting the label tags. We do this step   to       not over fit the data
   - Iterate until  ![equation](https://latex.codecogs.com/gif.latex?%7C%5Cmu%5E%7Bnew%7D_j-%5Cmu%5E%7Bold%7D_j%7C)
      - Assign each document x<sub>i</sub> to its closest mean vector μ<sub>j</sub>.
      - Update each mean vector μ<sub>j</sub> to be the mean of the x<sub>i</sub>’s assigned to it.

Distance between documents and mean are calculated using Cosine Similarity (since the documents are normalized according to their length). An error function is used as Gradient descent and the objective is to minimize this error function. It is the sum of the distance between the documents to their assigned clusters.

<u>Error Function</u>:

![equation](https://latex.codecogs.com/gif.latex?E%28D%2CM%29%20%3D%20%5Csum_%7Bi%3D1%7D%5E%7BN%7D%5Csum_%7Bj%3D1%7D%5E%7BN%7Dr_%7Bij%7D%20.%20d%28x_i%2C%5Cmu_j%29)

<b>3. K-Nearest Neighbor:</b>

The model for kNN is the entire training dataset. When a prediction is required for a unseen data instance, the kNN algorithm will search through the training dataset for the k-most similar instances. The prediction attribute of the most similar instances is summarized and returned as the prediction for the unseen instance. The decision rule in kNN can be written as:


![equation](https://latex.codecogs.com/gif.latex?knn%28x%2Cc_i%29%20%3D%20%5Csum_%20sim%28x%2Cd_j%29%20.%20knn%28x_i%2C%5Cmu_j%29)


These methods are used to find relevance of a given document to a query or retrieving a set a pages.

We also implement PageRank to rank pages according to their popularity once we find a set of pages relevant to the user.

We use Google's page rank method to rank pages which deals with spider traps and deadends.

Equation:

![equation](http://www.ccs.neu.edu/home/ekanou/ISU535.09X2/Homeworks/hw.03_files/pr_formula.jpg)


