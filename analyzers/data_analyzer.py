def analyze_data(data_list: list) -> list:
    """
    수집된 데이터 중 신뢰할 만한 데이터만 필터링하여 반환합니다.
    이 예시에서는 모델과 가격 정보가 모두 존재하는 데이터만 신뢰할 수 있다고 판단합니다.
    """
    trusted_data = []
    for data in data_list:
        if data.get('price') and data.get('model'):
            trusted_data.append(data)
    return trusted_data
