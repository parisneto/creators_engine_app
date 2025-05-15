Channel tags


# -*- coding: utf-8 -*-

# Sample Python code for youtube.channels.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.channels().list(
        part="brandingSettings",
        id="UCKHhA5hN2UohhFDfNXB_cvQ"
    )
    response = request.execute()

    print(response)

if __name__ == "__main__":
    main()


great, didnt now this part name !

This a sample response, from channel :

{
"kind": "youtube#channelListResponse",
"etag": "t0Apc1VGYF7Lw1VKqsIZ01ThJQs",
"pageInfo": {
"totalResults": 1,
"resultsPerPage": 5
},
"items": \[
{
"kind": "youtube#channel",
"etag": "LSaaQ3Pr0F9OgSEn4KP1xraefzc",
"id": "UCKHhA5hN2UohhFDfNXB\_cvQ",
"brandingSettings": {
"channel": {
"title": "Manual do Mundo",
"description": "Olá! Somos o Manual do Mundo e viemos mostrar que há sempre um caminho mais interessante e divertido para aprender sobre as coisas ao nosso redor. Oferecemos produtos e conteúdos criativos que promovem experiências únicas de entretenimento e aprendizagem, no físico e no digital, sozinhos ou acompanhados.\n\nAcreditamos que o conhecimento é capaz de eliminar qualquer obstáculo do caminho e é construído de um jeito colaborativo. É por isso que a melhor jornada é a que se anda junto, trocando descobertas, agregando mais gente.\n\nNosso ponto de partida é a curiosidade, e o de chegada também, porque quando a gente descobre uma resposta, nosso horizonte se expande, e a gente faz ainda mais perguntas. É assim que conquistamos o mundo!\n\nManual do Mundo. Desbravadores do conhecimento.\n\n- DÚVIDAS: [contato@manualdomundo.com.br](mailto:contato@manualdomundo.com.br)\n- PATROCÍNIOS e PARCERIAS: [comercial@manualdomundo.com.br](mailto:comercial@manualdomundo.com.br)\n- ASSESSORIA de IMPRENSA: [comunicacao@manualdomundo.com.br](mailto:comunicacao@manualdomundo.com.br)",
"keywords": ""como fazer" dicas experiências química física instruções truque howto "como hacer" "faça você mesmo" tutorial "how to" charada adivinhação como fazer palitos de fósforo "palitos de fósforo" brincadeiras bar "brincadeiras de bar" trick jogo",
"trackingAnalyticsAccountId": "UA-474540-6",
"unsubscribedTrailer": "5DLEBfN51BQ",
"country": "BR"
},
"image": {
"bannerExternalUrl": "[https://yt3.googleusercontent.com/F6lSy97NCPTI-gkbpNEsFowXrCi6TgpZWRFo3A8QEDhnhSNqtb6lbLRbfgw25egYIUZH6ZWI](https://yt3.googleusercontent.com/F6lSy97NCPTI-gkbpNEsFowXrCi6TgpZWRFo3A8QEDhnhSNqtb6lbLRbfgw25egYIUZH6ZWI)"
}
}
}
]
}

and here is a video snippet from the same channel :

{
"kind": "youtube#videoListResponse",
"etag": "OLUuGnfME1jw8\_O-L0wPxWSyLrc",
"items": \[
{
"kind": "youtube#video",
"etag": "30DH0T7FueHIl0\_F1lrEMUcJ4Ac",
"id": "5DLEBfN51BQ",
"snippet": {
"publishedAt": "2025-05-06T20:00:03Z",
"channelId": "UCKHhA5hN2UohhFDfNXB\_cvQ",
"title": "MIRAGEM EXISTE e podemos PROVAR!",
"description": "O que é miragem? Já ouviu falar que seriam delírios de alguém morrendo de sede? Ou já viu aquela “poça d’água” no asfalto em um dia de calor? Pois é… nada disso é alucinação. A miragem existe de verdade — e a explicação está na física!\n\nA luz pode se curvar ao atravessar camadas de ar com temperaturas diferentes, criando um reflexo do céu no chão. Parece água, dá a impressão de que está molhado… mas, na verdade, é como se o chão virasse um espelho refletindo o azul do céu.\n\n#Miragem #Física #Ciência #Refração #Reflexo #Óptica #Deserto #Experimento\n\nSeja membro deste canal e ganhe benefícios:\nhttps\://youtube.com/channel/UCKHhA5hN2UohhFDfNXB\_cvQ/join\n\n► Inscreva-se: [https://youtube.com/user/iberethenorio?sub\_confirmation=1\n►](https://youtube.com/user/iberethenorio?sub_confirmation=1\n►) Canal de cortes: [https://youtube.com/channel/UCzBTlYfHYMwVEru4hmLM8hg\n\nREDES](https://youtube.com/channel/UCzBTlYfHYMwVEru4hmLM8hg\n\nREDES) SOCIAIS\nInstagram: [http://instagram.com/manualdomundo\nTikTok](http://instagram.com/manualdomundo\nTikTok): [https://www.tiktok.com/@manualdomundo\nFacebook](https://www.tiktok.com/@manualdomundo\nFacebook): [http://facebook.com/manualdomundo\n](http://facebook.com/manualdomundo\n) \nInstagram Mari: [http://instagram.com/amarifulfaro\nTwitter](http://instagram.com/amarifulfaro\nTwitter) Iberê: [http://twitter.com/iberethenorio\n\nDúvidas](http://twitter.com/iberethenorio\n\nDúvidas) e sugestões: [contato@manualdomundo.com.br](mailto:contato@manualdomundo.com.br)\nImprensa e convites: [assessoria@manualdomundo.com.br](mailto:assessoria@manualdomundo.com.br)\nNegócios: [comercial@manualdomundo.com.br](mailto:comercial@manualdomundo.com.br)\n\nCRÉDITOS\nDireção e apresentação: Iberê Thenório \nDireção executiva: Mari Fulfaro\nDireção de Conteúdo: Fernando A. Souza \nDireção de Produção: Tiago César Silva\nProdução: Daniel Pedroso, Lucas Vallado\nCâmera: Jansen Bispo dos Santos\nEdição e finalização de imagens: Cris Poveda\n\nCopyright© Manual do Mundo®. Todos os direitos reservados.",
"thumbnails": {
"default": {
"url": "[https://i.ytimg.com/vi/5DLEBfN51BQ/default.jpg](https://i.ytimg.com/vi/5DLEBfN51BQ/default.jpg)",
"width": 120,
"height": 90
},
"medium": {
"url": "[https://i.ytimg.com/vi/5DLEBfN51BQ/mqdefault.jpg](https://i.ytimg.com/vi/5DLEBfN51BQ/mqdefault.jpg)",
"width": 320,
"height": 180
},
"high": {
"url": "[https://i.ytimg.com/vi/5DLEBfN51BQ/hqdefault.jpg](https://i.ytimg.com/vi/5DLEBfN51BQ/hqdefault.jpg)",
"width": 480,
"height": 360
},
"standard": {
"url": "[https://i.ytimg.com/vi/5DLEBfN51BQ/sddefault.jpg](https://i.ytimg.com/vi/5DLEBfN51BQ/sddefault.jpg)",
"width": 640,
"height": 480
},
"maxres": {
"url": "[https://i.ytimg.com/vi/5DLEBfN51BQ/maxresdefault.jpg](https://i.ytimg.com/vi/5DLEBfN51BQ/maxresdefault.jpg)",
"width": 1280,
"height": 720
}
},
"channelTitle": "Manual do Mundo",
"tags": \[
"como fazer",
"como funciona",
"experiência",
"ciência",
"mari fulfaro",
"iberê thenorio",
"Educação",
"Curiosidades",
"Experimentos",
"DIY",
"manual do mundo",
"miragem",
"deserto",
"física",
"optica",
"ilusão"
],
"categoryId": "28",
"liveBroadcastContent": "none",
"defaultLanguage": "pt",
"localized": {
"title": "MIRAGEM EXISTE e podemos PROVAR!",
"description": "O que é miragem? Já ouviu falar que seriam delírios de alguém morrendo de sede? Ou já viu aquela “poça d’água” no asfalto em um dia de calor? Pois é… nada disso é alucinação. A miragem existe de verdade — e a explicação está na física!\n\nA luz pode se curvar ao atravessar camadas de ar com temperaturas diferentes, criando um reflexo do céu no chão. Parece água, dá a impressão de que está molhado… mas, na verdade, é como se o chão virasse um espelho refletindo o azul do céu.\n\n#Miragem #Física #Ciência #Refração #Reflexo #Óptica #Deserto #Experimento\n\nSeja membro deste canal e ganhe benefícios:\nhttps\://youtube.com/channel/UCKHhA5hN2UohhFDfNXB\_cvQ/join\n\n► Inscreva-se: [https://youtube.com/user/iberethenorio?sub\_confirmation=1\n►](https://youtube.com/user/iberethenorio?sub_confirmation=1\n►) Canal de cortes: [https://youtube.com/channel/UCzBTlYfHYMwVEru4hmLM8hg\n\nREDES](https://youtube.com/channel/UCzBTlYfHYMwVEru4hmLM8hg\n\nREDES) SOCIAIS\nInstagram: [http://instagram.com/manualdomundo\nTikTok](http://instagram.com/manualdomundo\nTikTok): [https://www.tiktok.com/@manualdomundo\nFacebook](https://www.tiktok.com/@manualdomundo\nFacebook): [http://facebook.com/manualdomundo\n](http://facebook.com/manualdomundo\n) \nInstagram Mari: [http://instagram.com/amarifulfaro\nTwitter](http://instagram.com/amarifulfaro\nTwitter) Iberê: [http://twitter.com/iberethenorio\n\nDúvidas](http://twitter.com/iberethenorio\n\nDúvidas) e sugestões: [contato@manualdomundo.com.br](mailto:contato@manualdomundo.com.br)\nImprensa e convites: [assessoria@manualdomundo.com.br](mailto:assessoria@manualdomundo.com.br)\nNegócios: [comercial@manualdomundo.com.br](mailto:comercial@manualdomundo.com.br)\n\nCRÉDITOS\nDireção e apresentação: Iberê Thenório \nDireção executiva: Mari Fulfaro\nDireção de Conteúdo: Fernando A. Souza \nDireção de Produção: Tiago César Silva\nProdução: Daniel Pedroso, Lucas Vallado\nCâmera: Jansen Bispo dos Santos\nEdição e finalização de imagens: Cris Poveda\n\nCopyright© Manual do Mundo®. Todos os direitos reservados."
},
"defaultAudioLanguage": "pt"
}
}
],
"pageInfo": {
"totalResults": 1,
"resultsPerPage": 1
}
}

in this case I See no inclusion of the channel tags in the video, did I got something wrong ?





          "keywords": "\"como fazer\" dicas experiências química física instruções truque howto \"como hacer\" \"faça você mesmo\" tutorial \"how to\" charada adivinhação como fazer palitos de fósforo \"palitos de fósforo\" brincadeiras bar \"brincadeiras de bar\" trick jogo",
x

 "tags": [
          "como fazer",
          "como funciona",
          "experiência",
          "ciência",
          "mari fulfaro",
          "iberê thenorio",
          "Educação",
          "Curiosidades",
          "Experimentos",
          "DIY",
          "manual do mundo",
          "miragem",
          "deserto",
          "física",
          "optica",
          "ilusão"
        ],




Libraries & Techniques
pandas for DataFrame handling

collections.Counter for fast tag counting

.quantile() (via pandas/NumPy) to pick your percentile cutoff

(Optional) NLTK/regex to normalize (remove punctuation, accents)

(Optional) fuzzywuzzy or RapidFuzz to merge near-duplicate tags before counting




import pandas as pd
from collections import Counter

# assume df has columns: 'video_id', 'title', 'description', 'tags'
# where tags is a Python list of strings

# 1) flatten all tags
all_tags = [tag.lower().strip()
            for tags in df['tags']
            for tag in tags]

# 2) count frequencies
tag_counts = Counter(all_tags)
count_df = pd.DataFrame.from_dict(tag_counts, orient='index', columns=['count'])

# 3) pick your threshold (e.g. upper quartile)
threshold = count_df['count'].quantile(0.75)
common_tags = set(count_df[count_df['count'] >= threshold].index)

# 4) build exclusive_tags per video
def make_exclusive(video_tags):
    norm = [t.lower().strip() for t in video_tags]
    return [t for t in norm if t not in common_tags]

df['exclusive_tags'] = df['tags'].apply(make_exclusive)

# now df.exclusive_tags has only the “rare” or video-specific tags


LLM prompt template
Once you have exclusive_tags, you can feed each video into an LLM like this:


Vídeo:
- Título: "{title}"
- Descrição: "{description}"
- Tags exclusivas atuais: {exclusive_tags}

Em Português do Brasil, por favor:
1. Para cada tag em “Tags exclusivas atuais”, proponha:
   a) 2–3 sinônimos naturais
   b) possíveis grafias alternativas ou erros comuns de digitação
2. Com base no título e na descrição, sugira 5–10 novas tags relevantes que aumentem a chance de descoberta.
3. Retorne tudo no seguinte formato JSON:

{
  "synonyms": {
    "<tag1>": ["sin1", "sin2", ...],
    ...
  },
  "misspellings": {
    "<tag1>": ["erro1", "erro2", ...],
    ...
  },
  "new_tags": ["tagNova1", "tagNova2", ...]
}
