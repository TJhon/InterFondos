import datetime
import pandas as pd

SAVE_INTEBANK = "data/interbank"
funds = "interfondos_funds_name.csv"

# text_last_string: de A-D, incluido el "-"
def extract_last_element(text):
    last_word = text[-1]
    # print(last_word)
    if last_word in ["A", "B", "C", "D", "-"]:
        return last_word
    else:
        return "undefined"


data = pd.read_csv(f"{SAVE_INTEBANK}/{funds}")  # .head(2)
data["text_last_string"] = data["text"].apply(extract_last_element)
# print(data)


# value,text,moneda
# 22,IF Libre Disponibilidad Soles FMIV-A,Soles
# 22,IF Libre Disponibilidad Soles FMIV-B,Soles
# 22,IF Libre Disponibilidad Soles FMIV-C,Soles
# 24,IF Libre Disponibilidad FMIV-C,Dólares
# 01,IF Mixto Balanceado FMIV-,Dólares
# 20,IF Inversión Global FMIV-,Dólares
# API_CALL = 'https://api.interfondos.com.pe/api/mutual-fund/page/get-result-historic-calculator/{31}/{-}/{2024-10-15}/{2024-11-26}'
# date format yyyy-mm-dd


import requests, tqdm

a = data.head(1).to_dict("records")

API_CALL = "https://api.interfondos.com.pe/api/mutual-fund/page/get-result-historic-calculator/{value}/{text_last_string}/{initial_date}/{end_date}"


def get_data_fund(api_url, moneda, full_name):
    result = requests.get(api_url).json()
    result["moneda"] = moneda
    result["full_name"] = full_name
    daily_values = []
    if not result["hasError"]:
        result = result["result"]
        for date, value in zip(result["dates"], result["values"]):
            daily_values.append(
                {"fundName": result["fundName"], "date": date, "value": value}
            )
        data_result = pd.DataFrame(daily_values)
        data_result["moneda"] = moneda
        data_result["name_in_interfondos"] = full_name
        return data_result


current_date = datetime.date.today().strftime("%Y-%m-%d")
data_list = []
for i, row in data.iterrows():
    row_call = API_CALL.format(
        value=str(row["value"]).zfill(2),
        text_last_string=row["text_last_string"],
        initial_date="1900-01-01",
        end_date=current_date,
    )
    data_i = get_data_fund(row_call, row["moneda"], row["text"])
    data_list.append(data_i)


result = pd.concat(data_list, ignore_index=True)

result.to_csv("data/interbank/interfondos_data.csv", index=False)
