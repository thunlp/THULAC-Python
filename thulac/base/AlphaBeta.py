import time

class AlphaBeta:
    value = 0
    nodeId = 0
    labelId = 0

    def __init__(self):
        self.value = 0
        self.nodeId = -2
        self.labelId = 0

    def dbDecode(self, l_size, llWeights, nodeCount, nodes, values, alphas, result, preLabels, allowedLabelLists):
        nodeId = 0
        pNodeId = []
        pPreLabel = []
        pAllowedLabel = []
        k = 0
        j = 0
        tmp = AlphaBeta()
        best = (0, -1, 0)
        preAlpha = AlphaBeta()
        
        score = 0 
        index = 0
        index2 = 0
        index3 = 0
        
        for i in range(nodeCount):
            alphas.append({})

            pAllowedLabel = allowedLabelLists[i]
            for j in pAllowedLabel:
                if(j == -1):
                    break
                tmp = (0, -2, 0)
                nodeId = nodes[i].predecessors
                pPreLabel = preLabels[j]
                if(nodeId >= 0):
                    for k in pPreLabel:
                        if(k == -1):
                            break
                        if(k not in alphas[nodeId]):
                            continue
                        preAlpha = alphas[nodeId][k]

                        if(preAlpha[1] == -2):
                            continue
                        score = preAlpha[0] + llWeights[k*l_size + j]

                        if((tmp[1] < 0) or (score > tmp[0])):
                            tmp = (score, nodeId, k)

                if((nodes[i].type == 1) or (nodes[i].type == 3)):
                    tmp = (tmp[0] + values[i*l_size + j], -1, tmp[2])
                else:
                    tmp = (tmp[0] + values[i*l_size + j], tmp[1], tmp[2])
                if(nodes[i].type >= 2):
                    if((best[1] == -1) or best[0] < tmp[0]):
                        best = (tmp[0], i, j)

                alphas[i][j] = tmp
        tmp = best
        while(tmp[1] >= 0):
            result[tmp[1]] = tmp[2]
            if(tmp[2] in alphas[tmp[1]]):
                tmp = alphas[tmp[1]][tmp[2]]
            else:
                break
        return best[0]
