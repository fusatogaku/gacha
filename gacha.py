import random, copy, sys

def getDataFromDB():
    """
    データベースからガチャに必要なデータを取得する。

    Returns
    -------
    info :
        レアリティと排出率を格納したlist型の二次元データ。
    master :
        排出される景品の名称と景品のレアリティを格納した辞書型データ。
    """
    # ガチャ自体(レアリティ、確率)のデータ
    info = {
        'weights': [[5, 0.03], [4, 0.15], [3, 0.82]],
        'pickup': [['大当たり!!01', 0.4], ['大当たり!!02', 0.4], ['当たり!01', 0.5]]
    }
    # ガチャの景品のデータ
    master = [
        {'Goods': '大当たり!!01', 'rarity': 5},
        {'Goods': '大当たり!!02', 'rarity': 5},
        {'Goods': '大当たり!!03', 'rarity': 5},
        {'Goods': '大当たり!!04', 'rarity': 5},
        {'Goods': '当たり!01', 'rarity': 4},
        {'Goods': '当たり!02', 'rarity': 4},
        {'Goods': '当たり!03', 'rarity': 4},
        {'Goods': '当たり!04', 'rarity': 4},
        {'Goods': '当たり!05', 'rarity': 4},
        {'Goods': '当たり!06', 'rarity': 4},
        {'Goods': 'はずれ01', 'rarity': 3},
        {'Goods': 'はずれ02', 'rarity': 3},
        {'Goods': 'はずれ03', 'rarity': 3},
        {'Goods': 'はずれ04', 'rarity': 3},
        {'Goods': 'はずれ05', 'rarity': 3},
        {'Goods': 'はずれ06', 'rarity': 3},
        {'Goods': 'はずれ07', 'rarity': 3},
        {'Goods': 'はずれ08', 'rarity': 3},
        {'Goods': 'はずれ09', 'rarity': 3},
        {'Goods': 'はずれ10', 'rarity': 3},
    ]

    return [info, master]

def getConfig():
    """
    ガチャで使用する設定データを取得・まとめる。

    Return
    ------
    config :
        レアリティごとに排出率、ピックアップ景品、景品をまとめた辞書型データ。
        'rarity': レアリティ。int型。
        'prob': レアリティごとの排出率の合計。float型。
        'pikcups': ピックアップ対象の景品とピックアップ確率。list型の二次元配列。
        'ids': レアリティごとの景品。list型。
    """
    config = [] # 設定データ
    info, master = getDataFromDB()
    rarity = [] 
    prob = []
    
    # レアリティ、排出確率を分離
    for i in info['weights']:
        rarity.append(i[0])
        prob.append(i[1])

    # configにレアリティ、確率、ピックアップ対象、景品を詰める。
    for i in range(len(rarity)):
        config.append({'rarity': rarity[i], 'prob': prob[i], 'pickups':[] , 'ids':[]})
        
        for ids in filter(lambda x: x['rarity'] == rarity[i], master):
            for pickups in filter(lambda y: ids['Goods'] in y , info['pickup']):
                config[i]['pickups'].append(pickups)

            config[i]['ids'].append(ids['Goods'])

    return config

def normalize(confSrc):
    """
    設定データの排出率の正規化を行う。

    Parameter
    ---------
    confSrc :
        正規化する設定データ。getConfig()で作成されたデータを、
        レアリティを指針として、選定したデータ。
    
    Returns
    -------
    ret :
        レアリティごとの排出率を正規化した設定データ。
    """
    ret = []
    summed = sum(entry['prob'] for entry in confSrc)
    for entry in confSrc:
        entry['prob'] = entry['prob'] / summed
        ret.append(entry)

    return ret

def createTable(config):
    """
    設定データから、ピックアップを加味したそれぞれの景品の排出率をテーブルとして加工する。

    Parameter
    ---------
    config :
        ガチャの設定データ。getConfig()で作成されたデータを渡す。
    
    Returns
    ------
    cid :
        ガチャの景品単体。
    prob :
        景品それぞれの排出率。
    entry['rarity'] :
        景品のレアリティ。
    """
    table = []

    for entry in config:
        prob = entry['prob']
        acc = 0
        for i in entry['pickups']:
            if i: acc += i[1]

        if acc > 0:
            pickProb = prob * acc
        else: pickProb = 0
        nonPickProb = (prob - pickProb) / (len(entry['ids']) - len(entry['pickups']))

        for cid in entry['ids']:
            searched = []
            for pick in entry['pickups']:
                if cid in pick[0]:
                    searched = pick
                    break
                else: searched = False

            if searched:
                prob = entry['prob'] * searched[1]
            else: prob = nonPickProb
            table.append([cid, prob, entry['rarity']])

    return table

def createTableCeil(conf):
    """
    天井回数に達したガチャ用のテーブルを作成する。

    Parameter
    ---------
    conf : 
        ガチャの設定データ。getConfig()で作成されたデータを渡す。
    
    Returns
    -------
    table :
        normalize関数を使い、天井用に加工した設定データで作成したテーブル。
    """
    print('createCeil')
    confSrc = copy.deepcopy(conf) # normalize関数の影響で、元のconfigデータが書き変わるのでdeepcopyで回避。
    filtered = normalize(list(map(lambda x: x, (filter(lambda x: x['rarity'] == 5, confSrc)))))
    return createTable(filtered)

def createTableRescue(conf):
    """
    10連ガチャで保証されているレアリティを弾けなかった場合、保証用のテーブルを作成する。

    Parameter
    ---------
    conf : 
        ガチャの設定データ。getConfig()で作成されたデータを渡す。
    
    Returns
    -------
    table :
        normalize関数を使い、保証用に加工した設定データで作成したテーブル。
    """    
    print('createRescue')
    confSrc = copy.deepcopy(conf) # normalize関数の影響で、元のconfigデータが書き変わるのでdeepcopyで回避。
    filtered = normalize(list(map(lambda x: x, (filter(lambda x: x['rarity'] > 3, confSrc)))))
    return createTable(filtered)

def gachaInternal(config, user, rval):
    """
    ガチャの実行関数。パターンに応じてどのテーブルで作成するか選定する。

    Parameters
    ----------
    config :
        ガチャの設定データ。getConfig()で作成されたデータを渡す。
    user :
        ユーザの持つ辞書型データ。
        'ceilCount': 最高レアレティを引けなかった回数。デフォルトは 0 に設定する。
        'rescue': 保証対応が必要かどうかの判定。デフォルトは False を設定する。
    rval :
        ガチャ当選の指針となる、0 ~ 1.0のfloat型。
        基本的にはランダムな値を与える。

    Returns
    -------
    resultID :
        当選した景品。
    rarity :
        当選した景品のレアリティ。
    ceilCount :
        最高レアレティを引けなかった回数。rarityが天井条件のレアリティの場合、0 が返却される。
    """

    ceilCount = user['ceilCount'] if user['ceilCount']  else 0

    table = createTableCeil(config) if ceilCount == 89 \
        else createTableRescue(config) if user['rescue'] \
        else createTable(config)

    accum = 0
    for field in table:
        accum += field[1] # probを足し上げる。
        if rval < accum: return field[0], field[2], ceilCount
    raise ValueError("やり直してください")

def gacha(config, user, rval):
    """
    単発ガチャの実行関数。gachaInternal()を、単発用に実行する。

    Parameters
    ----------
    config :
        ガチャの設定データ。getConfig()で作成されたデータを渡す。
    user :
        ユーザの持つ辞書型データ。
        'ceilCount': 最高レアレティを引けなかった回数。デフォルトは 0 に設定する。
        'rescue': 保証対応が必要かどうかの判定。デフォルトは False を設定する。
    rval :
        ガチャ当選の指針となる、0 ~ 1.0のfloat型。
        基本的にはランダムな値を与える。

    Returns
    -------
    resultID :
        当選した景品。
    ceilCount :
        最高レアレティを引けなかった回数。rarityが天井条件のレアリティの場合、0 が返却される。
    """
    resultID, rarity, ceilCount = gachaInternal(config, user, rval)
    ceilCount = 0 if rarity == 5 else user['ceilCount'] + 1
    return [resultID, ceilCount]

def gacha10(config, user, rvals):
    """
    10連ガチャの実行関数。gachaInternal()を、10連用に実行する。

    Parameters
    ----------
    config :
        ガチャの設定データ。getConfig()で作成されたデータを渡す。
    user :
        ユーザの持つ辞書型データ。
        'ceilCount': 最高レアレティを引けなかった回数。デフォルトは 0 に設定する。
        'rescue': 保証対応が必要かどうかの判定。デフォルトは False を設定する。
    rval :
        ガチャ当選の指針となる、0 ~ 1.0のfloat型。
        基本的にはランダムな値を与える。

    Returns
    -------
    resultID :
        当選した景品。
    ceilCount :
        最高レアレティを引けなかった回数。rarityが天井条件のレアリティの場合、0 が返却される。
    """
    ids = []
    ceilCount = user['ceilCount']
    over4 = False # 保証内かどうかの真偽式。

    for i in range(len(rvals)):
        rescue = True if i == len(rvals) - 1 and over4 == False else False
        resultID, rarity, ceilCount = gachaInternal(config, {'ceilCount': ceilCount, 'rescue': rescue}, rvals[i])
        ceilCount = 0 if rarity == 5 else ceilCount + 1
        if rarity > 3:
            over4 = True
        ids.append(resultID)
    
    return [ids, ceilCount]

# 実行
if __name__ == '__main__':
    
    config = getConfig()
    if sys.argv[1] == 'normal':
        print('単発ガチャ(通常) -> ', gacha(config, {'ceilCount': 0, 'rescue': False}, random.random()))
    elif sys.argv[1] == 'ceil':
        print('単発ガチャ(天井) -> ', gacha(config, {'ceilCount': 89, 'rescue': False}, random.random()))
    elif sys.argv[1] == 'rescue':
        print('単発ガチャ(保証ガチャ) -> ', gacha(config, {'ceilCount': 0, 'rescue': True}, random.random()))
    elif sys.argv[1] == 'ten':
        rvals = [random.random() for i in range(10)]
        print('10連ガチャ -> ', gacha10(config, {'ceilCount': 0, 'rescue': False}, rvals))

