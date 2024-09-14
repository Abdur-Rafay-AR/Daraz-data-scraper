import requests
import json
from bs4 import BeautifulSoup

key = input("Enter the Keyword:")
print("Please wait patiently...")
data = []
t = True
tr = True
headers = {
    'authority': 'www.daraz.pk',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.daraz.pk/catalog/?q=hello&_keyori=ss&from=input&spm=a2a0e.searchlist.search.go.3ac940e9laUEBs',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}

params ={
        'q': key,
        '_keyori': 'ss',
        'from': 'input',
        'spm': 'a2a0e.searchlist.search.go.6f046735E5sf9x',
        }
current_page = 1
response = requests.get('https://www.daraz.pk/catalog/', params=params, headers=headers)
soup = BeautifulSoup(response.content, "lxml")
tags = soup.find_all("script")[3].text
tag = eval(tags[16:].replace("false", "False").replace("true", "True"))
if 'mods'in tag and 'listItems' in tag['mods']:
    while tr:
        try:
            pg_link = str(soup.find_all("link")[4]).replace('<link href="','').replace('" rel="next"/>','')[:-1] + str(current_page)
            response = requests.get(pg_link, params=params, headers=headers)
        except:
            pass
        for i in tag['mods']['listItems']:
            url = "https:"+i['productUrl']
            response1 = requests.get(url, headers=headers)
            s1 = BeautifulSoup(response1.content, "lxml")    
            s2 = soup.find_all("script")[3].text
            s3 = eval(s2[16:].replace("false","False").replace("true","True"))
            page_size = s3['mainInfo']['pageSize']
            total_result = int(s3['mainInfo']['totalResults'])
            total_pages = int((int(total_result))/(int(page_size)))
            if t:
                print("Total Pages:",total_pages)
                t = False
            for j in s3['mods']['listItems']:
                js= {
                    "product_name" :'',
                    "brand":'',
                    "description":'',
                    "Rating_distribution":
                    {


                    },
                    "free_shipping":'',
                    "SKU":'',
                    "Breadcrum" : '',
                    "product_url" : url,
                    "Total_Ratings" : '',
                    "Rating" :'',
                    "Original_price" :'',              
                    "discount_percent" :'',
                    "discount_price":'',
                    "image_urls" :'',
                    "positive_seller_rating":'',
                    "chat_response":'',
                    "store_name":'',
                    "store_link":'',
                    "ship_on_time":'',
                    "warranty":'',
                    "return":''
                                
                }

                js['product_name'] = j['name']
                js['description'] = j['description']
                js['Original_price']  = j['utLogMap']['originalPrice']
                js['discount_price'] = j['price']
                js['discount_percent'] = j['utLogMap']['discount']+"%"
                js['brand'] = j['brandName']
                try:
                    js['Rating'] = j['ratingScore']
                    js['Total_Ratings'] = j['review']
                except:
                    pass
                js['image_urls'] = j['image']
                js['store_name'] = j['sellerName']
                js['free_shipping'] = j['utLogMap']['isFreeShipping']
                js['SKU']  = j['addToCartSkus'][0]['sku']
                s4 = [x for x in s1.find_all("script") if "window.LZD_RETCODE_PAGENAME" in x.text][0]
                s5 = eval(s4.text.split("app.run(")[-1].split("} catch(e)")[0].rsplit(");",1)[0].replace("false","False").replace("true","True"))
                ratings = s5['data']['root']['fields']['review']['ratings']['scores']
                js['Rating_distribution']["1-star"] = ratings[4]
                js['Rating_distribution']["2-star"] = ratings[3]
                js['Rating_distribution']["3-star"] = ratings[2]
                js['Rating_distribution']["4-star"] = ratings[1]
                js['Rating_distribution']["5-star"] = ratings[0]
                try:
                    js['chat_response'] = s5['data']['root']['fields']['seller']['chatResponsiveRate']['value']
                    js['positive_seller_rating'] = s5['data']['root']['fields']['seller']['positiveSellerRating']['value']
                    js['ship_on_time'] = s5['data']['root']['fields']['seller']['shipOnTime']['value']
                    warranty = s5['data']['root']['fields']['warranties']
                    js['warranty'] = str(warranty).split('{}, ')[-1].split("'")[3]
                    js['return'] = str(warranty).split('{}, ')[-2].split("'")[7]
                    js['store_link'] = s5['data']['root']['fields']['seller']['url']
                except:
                    pass
                bread = s5['data']['root']['fields']['skuInfos']
                bread1 = list(bread.keys())[0]
                js['Breadcrum'] = bread[bread1]['dataLayer']['pdt_category']  
                data.append(js)
        
            if current_page <= 3:
                print("Current Page:",current_page)
                current_page+=1
                continue
            else:
                tr = False
                break
    out={
            "keyword": key,
            "total_Pages": total_pages,
            "total_Items": total_result,
            "products": data
        }
    with open("data.json","w") as fl:
        json.dump(out, fl, indent=4)
        fl.close()
else:
    print("No data found!")