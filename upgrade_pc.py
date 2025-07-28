import asyncio
import httpx
import re
import gspread
import telegram
import os
from lxml import html
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# =============== CARREGA VARIÁVEIS DE AMBIENTE ===============
# Garanta que você tem um arquivo .env na mesma pasta do script
load_dotenv()

# =============== CONFIGURAÇÃO GOOGLE SHEETS ===============
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE_UPGRADE")
GOOGLE_SHEETS_NAME = os.getenv("GOOGLE_SHEETS_NAME_UPGRADE")
GOOGLE_SHEETS_WORKSHEET_UPGRADE = os.getenv("GOOGLE_SHEETS_WORKSHEET_UPGRADE")

creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEETS_NAME).worksheet(GOOGLE_SHEETS_WORKSHEET_UPGRADE)


# =============== CONFIGURAÇÃO TELEGRAM ===============
bot_token = os.getenv("TELEGRAM_BOT_TOKEN_UPGRADE")
chat_id = os.getenv("TELEGRAM_CHAT_ID_UPGRADE")
bot = telegram.Bot(token=bot_token)


# =============== LISTA DE ITENS ===============
# Lista de produtos para monitorar
itens = [
    # 🎮 GPUs
    {
        "nome": "RX 9060 XT 16GB",
        "preco_alvo": 2999,
        "urls": [
            "https://www.kabum.com.br/produto/870973/placa-de-video-xfx-rx-9060-xt-oc-amd-radeon-16gb-gddr6-128bits-20-gbps-triple-fan-rdna-4-rx-96ts316b7",
            "https://www.amazon.com.br/XFX-Radeon-9060XT-Triple-RX-96TS316BA/dp/B0F8128Y33/ref=sr_1_1?crid=2E464Z8HL4DDZ&dib=eyJ2IjoiMSJ9.h_wAakPRC-rPQbconyG8vU-Nh0treW2KJ1jU4E4XBmErfQCBh0k3rYet_NWd0XiYuLsigIvhVLiuKa7DLrJlhJSY4IfVWL1wNigaYOKKEahd94y8kYLr1eahgt6UAa1wGHBM5qJBoqKav1sriL-Vs-McQXYXYepHhMw3odGTBfozoiGdadhUa0t80Bw6HOf8vSLN8af6fLctDHFdnzvCxrkmSjsdusZc30ylkyUKjph3lc-BhWTPNEOWNazRjC22OmecK5VheqeaLOjk3AF9CKCcOap8VqUN1MbN8jh1Rg8.7Pi4CCm61eHUnBi1zVisfpA1X_CrSxrsd8LiNkW40wQ&dib_tag=se&keywords=rx+6900+xt+16gb&qid=1753710130&sprefix=RX+9060+XT%2Caps%2C346&sr=8-1&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147"
        ],
    },
    {
        "nome": "RX 9070 16GB",
        "preco_alvo": 3999,
        "urls": [
            "https://www.kabum.com.br/produto/690385/placa-de-video-asus-prime-rx-9070-xt-o16g-amd-radeon-16gb-gddr6-axial-tech-opengl-4-6-90yv0l71-m0na00",
            "https://www.amazon.com.br/GIGABYTE-RADEON-256BITS-GV-R9070XTGAMING-OC-16GD/dp/B0DT7B79K9/ref=sr_1_1?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=146CWLSMM4BVA&dib=eyJ2IjoiMSJ9.WOrYlE5wnJ7IXVVjlxXFTUvpdlsMj5M76QIpOdochp8IqihB4u826Q-1jiFNYeOSiQKTF8YfJO-XLhw9HP-uTBsnpsMkFwJEZ5N-p7bb8x2OQk9Cy3zRqJy0SGq3xDnOR4Cf6_E9poK9kRDS9-8YHcmIcXof5nSwClaSMwuUmcoeotHWxqICKjuC4nrfebv8QqVPkmNc7RxLpLBbFlZEw3X8kkAHaNMHuOIPojWTKWnT_vIC0qlyHHjzvANLLK8FCWS2oddMXx2-y6tgbGURKcRUlT3zlyoBMEryMo_Ed6E.2TBwumrBr7fl4BeBB-Mp-8obeFkH1f3IKVzy2puw02w&dib_tag=se&keywords=rx+9070+16gb&qid=1753710176&sprefix=rx+9070+16gb%2Caps%2C268&sr=8-1&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147",
        ],
    },
    # 🖥️ Monitores QHD/WQHD
    {
        "nome": 'Samsung Odyssey G5 27" QHD 165Hz',
        "preco_alvo": 1199,
        "urls": [
            "https://www.kabum.com.br/produto/713377/monitor-gamer-curvo-samsung-odyssey-g5-27-qhd-165hz-1ms-hdr10-freesync-hdmi-e-dp-preto-ls27cg552elmzd",
            "https://www.amazon.com.br/Monitor-Gamer-Samsung-Odyssey-G5/dp/B0DWQK1Q8S/ref=sr_1_5?crid=39OTUL4A34M4X&dib=eyJ2IjoiMSJ9.dB84mEHTo9Qyq9FugaLoLC8N1JpmNjM2HDAtKSeZ-kjXrZdnysIh2tJ1v125pU_4aB2Tu0_dunHcyDrHbFpcP7s1KK4losk5F4KXr2iJLfENRo_PvhtRYibWjCuKfZZFqU3vYs5N9XmqF07Bq6HGpBLl0eBYcgedxXfm8Byezye4E5Nijz0I5Zgtx9uZ-fRrPFCFVm8TG4OQNfsIjuAUauZytyJYGXHyjl23EUMQKGqdea90YkxdrH9KSNtMSI7G9HvkKySZJpUgZaKqqMyXmyDTiq52EiI6dIfENG8IO1I.qqo4w5yW5oQzqpx6LXafiofInHt_Z79VCnTjvkXqwZg&dib_tag=se&keywords=odyssey+g5+27+qhd+165hz&qid=1753710329&sprefix=odyssey+g5+27%2Caps%2C282&sr=8-5&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147"

        ],
    },
    {
        "nome": 'Samsung Odyssey G5 32" QHD 165Hz',
        "preco_alvo": 1519,
        "urls": [
            "https://www.kabum.com.br/produto/713376/monitor-gamer-curvo-samsung-odyssey-g5-32-qhd-165hz-1ms-hdr10-freesync-hdmi-e-dp-preto-ls32cg552elmzd",
            "https://www.amazon.com.br/Monitor-Gamer-Samsung-Odyssey-G5/dp/B0DWQNS8TN/ref=sr_1_3?crid=5SD56B7ITHTS&dib=eyJ2IjoiMSJ9.pl4I6RRqVzd-TrJYXMRIk4fJ5nc0IXznNJgrKa7S38jJHqZYDQcvJo53wRMJnyUULT0Wz6n7FKMRWYT-XTRT5GLhc-hsCOE0iL9KICxAFMAJuhZlRcd-g3sj8Jg0ZxGQMhLUOyXiVpjZCvo2wJJYxUdxGkNe_F9oHYBpu73dqj_6_8UTEN0QQ3vQRp4zuPX9-harXHY2PB6bqBEl7rakoCCLqgCBTmjPV97WcV8gVBWccCKybFMFmoyQ3ogBZL8ZqjS_ycMQDSFNMe_3A5OAQCPEDvPptmolfFAXIrWj49M.Qp_ZJQGHRbw6PK7x_u0BNQoJJZj1P6znyNxr2pJCRFw&dib_tag=se&keywords=odyssey+g5+32&qid=1753710414&sprefix=odyssey+g5+%2Caps%2C1968&sr=8-3&ufe=app_do%3Aamzn1.fos.a492fd4a-f54d-4e8d-8c31-35e0a04ce61e"
        ],
    },
    {
        "nome": 'LG Ultragear 27" QHD 180Hz',
        "preco_alvo": 1299,
        "urls": [
            "https://www.kabum.com.br/produto/620992/monitor-gamer-lg-ultragear-27-fhd-ips-180hz-1ms-gtg-hdr10-displayport-e-hdmi-g-sync-freesync-preto-27gs60f-b",
            "https://www.amazon.com.br/Monitor-Gamer-LG-UltraGear-OLED/dp/B0D8F4XP2C/ref=sr_1_7?crid=1SF4ZG9Y9X3L6&dib=eyJ2IjoiMSJ9.9EjNkQxzx8T_oFUKjHZokv7T7YB4zvsprNEGxV2y_5e5xPVBIns574zsVP5HCBXtHPt6Y2uB54Afn01laUTlBERU0GUcfuioAGpRFHBxp3dHMWdIbwprYDq-Z5dDNhkPjzCHWuARVz24GoejmdWArBORlSJ0cNMrR1H7xujVZTRtp49fpT3NdoQUmrcrAi-LXOLcX59IvP-ZtZ5F_tdtFxriEl0xpOkC1gZMm3XQePHHyYf5X4pTcucxv87lo3YFZ2XVjDH2MGTvBwAMJfRAunxhxUFFTb6mmOxpKx0k0R0.13F2T6UtWgbAkzmXtI6fBseIcKOVPHkwMfc0prNE814&dib_tag=se&keywords=ultragear+27+qhd&qid=1753710543&sprefix=ULTRAGEAR+27%2Caps%2C166&sr=8-7&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147",
        ],
    },
    {
        "nome": 'Samsung Odyssey G5 34" WQHD 100Hz',
        "preco_alvo": 1799,
        "urls": [
            "https://www.kabum.com.br/produto/613318/monitor-gamer-curvo-samsung-odyssey-g5-34-wqhd-ultrawide-165hz-1ms-hdmi-e-dp-freesync-premium-preto-lc34g55twwlmzd",
            "https://www.amazon.com.br/Monitor-Samsung-Odyssey-ultrawide-Freesync/dp/B0D3J76C63/ref=sr_1_2?crid=17NIL9AD2SPCT&dib=eyJ2IjoiMSJ9.LMEIiu3_AnovOArfWXTfes1tK1_7dUwicPjnRqBGPrvhTKPm2b1kQLV-A-LozI7IAKAJ0y8kG3mZn1gSDynO7J7bO563zyVanGgvh9-IfQmoCiSWpVTcp7ivB048x3ebYJxiVxZZCPz89QBSCMph4Mc4njtyKgf7sDeecFR0E6mnmQAoydzKdsvPWZ6-rdPLxaercBiqCBh_glbjd1bzFVCtp5vbaveuj3rJ0w8LvQyCSGwpEk8cxButxXuXelgNAkAWMKc-12J1VWdlrYHE9m6rP5y8sPoVZ_iqKchjUVg.YkqjHC6wMiiOsgb4mkabzAX1MKnPluo7gGh4WdaYii8&dib_tag=se&keywords=samsung+odyssey+g5+34&qid=1753710492&sprefix=odyssey+g5+34%2Caps%2C205&sr=8-2&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147"
        ],
    },
    # 💾 Memórias RAM DDR4 2x16GB
    {
        "nome": "Corsair Vengeance 2x16GB 3200 CL16",
        "preco_alvo": 399,
        "urls": [
            "https://www.kabum.com.br/produto/110828/memoria-ram-corsair-vengeance-lpx-32gb-2x16gb-3200mhz-ddr4-cl16-black-cmk32gx4m2e3200c16",
            "https://www.amazon.com.br/Corsair-Mem%C3%B3ria-computador-VENGEANCE-3200MHz/dp/B07RW6Z692/ref=sr_1_5?crid=2D2BXS1GEJJQE&dib=eyJ2IjoiMSJ9.uFy5t9sS2-ScI6oEpKAsrm2TMsfzVNHAuwf3D2ObvCTJjNmbfiDXJcPPhBxBMDOKfdKHCuwMD6-54HfPml8ceAzNyMQ1pAyd9pQb1W8EpAK_qFsy9qTMxLwMO_nuYN2blN-dqdWj2pzV314gEabMb4c7v4FaJiT3Bgt95fPJxn4qGPy9UQNtBZWxxUUizT2jZdR34NAgtktedSc9RZFcdv_PiVsnGxaZW5Uk1yixZP7TJw9Eb_S_NoiYqEtAOA33VobJ8YUQ3B-CTBylqIrwYqxRhvNyPnGSsNVUtKczTKs.0QRFK81CyLspuPhsYbbGAigA5-r9SM_shJpKchAtedE&dib_tag=se&keywords=corsair%2Bvengeance%2Blpx%2B32gb%2B2x16gb%2Bddr4%2B3200mhz&qid=1753710739&sprefix=VENGEANCE%2B32GB%2BDDR4%2Caps%2C1908&sr=8-5&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147&th=1"
        ],
    },
    {
        "nome": "Patriot Viper Steel 16GB 3200 CL16",
        "preco_alvo": 389,
        "urls": [
            "https://www.kabum.com.br/produto/381082/memoria-patriot-viper-steel-rgb-16gb-3200mhz-ddr4-cl18-udimm-pvsr416g320c8",
            "https://www.amazon.com.br/Patriot-Viper-Steel-S%C3%A9rie-M%C3%B3dulo/dp/B08N68G6XF/ref=sr_1_1?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=F1G8U5HLU842&dib=eyJ2IjoiMSJ9.BwmsDP39LX3ocv1En-SzPLXgXZTQcSVSBGteMcX1T_6cxo7NScJkW6OQ789QBXr6cn0Z4e8imRFrbc3_jqw8Hn62zXFycGTqgKW9cyfLFFniVssV5CwCx3MZ5CZM0BftVAHi68bOx8IPyb-NFKV9ZG1CQ6sZk_AF139BeKKgNKxt2ie2s03ezCfdAOFvixVFCvySkNZMgenoOS54xgJwCSWa_m2VVL7UaVBfDK0t_0LmBlsDBypRfZkJ1ZwlQTximsft6ZFLtWg6TbdF_Q_cyW-EaUMpLmQ1EYUFuZ9sfVg.bIJydKiq0oAINjIJ_LdtbiQGpZxbMYsqnYnVhdzZ5I8&dib_tag=se&keywords=PATRIOT+VIPER+STEEL+16GB+3200&qid=1753710820&sprefix=patriot+viper+steel+16gb+3200%2Caps%2C1232&sr=8-1&ufe=app_do%3Aamzn1.fos.e05b01e0-91a7-477e-a514-15a32325a6d6"
        ],
    },
    {
        "nome": "Kingston Fury Beast 2x16GB 3200 CL16",
        "preco_alvo": 399,
        "urls": [
            "https://www.kabum.com.br/produto/193569/memoria-ram-kingston-fury-beast-32gb-2x16gb-3600mhz-ddr4-cl18-preto-kf436c18bbk2-32",
            "https://www.amazon.com.br/Kingston-Sincroniza%C3%A7%C3%A3o-infravermelha-KF432C16BB12A-16/dp/B0CGLWRFQK/ref=sr_1_7?crid=1GPHHRV1XTN6M&dib=eyJ2IjoiMSJ9.9ruJdiyli_fBfRThITZP_V00IZ5GPThFuKqej3FKlVlZmVFlAtQJceyyImQ6dEy4xYQH5vLSUjomidW2fJV8qeKINL_4k3OnoBlq8fhyEhihUWlVapbrdVUnIzo5Q8hy4Rqs3QXYVZXh8nDW0yloJbFBS-8qcP0pRsHS5_FgRUa3DGNIOOQYnjY9BEbQ7uQGaEiuXmrlY4077NtUDk-fIqRZJpzugiTk6oYaE-wA1UuUPAPF-lo4SnVFVJ_smGKx0okaXMV5eXwagUh3oysFE3Kswx4kB8EKz6U2OS5kKRo.Netn9D0kLvYeYKVkneVVNCgMR5uYXsWIJS5AVm6cXak&dib_tag=se&keywords=kingston+fury+beast+32gb+2x16gb+ddr4+3200mhz+cl16&qid=1753710912&sprefix=fury+beast+32gb+ddr4%2Caps%2C430&sr=8-7&ufe=app_do%3Aamzn1.fos.e05b01e0-91a7-477e-a514-15a32325a6d6",
        ],
    },
    # 🖱️ Fans ARGB
    {
        "nome": "Lian Li UNI FAN SL-INF 120 kit 4",
        "preco_alvo": 499,
        "urls": [
            "https://www.kabum.com.br/produto/894985/fan-gamer-lian-li-uni-fan-sl-wireless-120-argb-branco?srsltid=AfmBOooCNG4pLMqXO5W6yrrivQPqU0_79By42CgZXfsDJ0R9BLlLpEprakw",
            "https://www.amazon.com.br/FAN-GAMER-UNI-SL-INF-BRANCO/dp/B0B4SJVQKY/ref=sr_1_1?crid=3T6K1ZK6PUWF9&dib=eyJ2IjoiMSJ9.XT_rY7oMWgTYe2bJM5dIgsyRUwB0kTNuf3EaE_imz41JKIP_RVjFcqssnN43PKKqFrtB7VwIN7y4eKBgyv5CLnv6Pb-ezQdi2HP1s7BXaTMhESqjqEoLgsmweK3lqiL-XyH51-CIMBUrh3MA9HaDl7FOW0yVfPO3bZAJRvw76U5u58wM49P9DcticdcAY1WupXr-dOu1-Zwalgco56-sfgctX_dFeGBdu2666hNk1KsCzo8_v6aygFjRPa4SZ908Z3R-bBqZzW9paATIGTpwkdaZ0DfaHGlmM1gL_f9g8RU.0fVZGGiYEKwLZ6qROnkr-5x0rOstrKlNd2WS45oqKgY&dib_tag=se&keywords=lian+li+uni+fan+sl-inf+120&qid=1753711099&sprefix=Lian+Li+UNI+FAN+SL-INF+120%2Caps%2C3792&sr=8-1&ufe=app_do%3Aamzn1.fos.fcd6d665-32ba-4479-9f21-b774e276a678"
        ],
    },
    {
        "nome": "DeepCool FK120 kit 3",
        "preco_alvo": 239,
        "urls": [
            "https://www.kabum.com.br/produto/479414/kit-fan-deepcool-fk120-120mm-preto-com-3-unidades-r-fk120-bknpf3-g-1",
        ],
    },
    {
        "nome": "Cooler Master Mobius kit 3",
        "preco_alvo": 479,
        "urls": [
            "https://www.kabum.com.br/produto/882982/kit-3-fan-cooler-master-mobius-120p-120mm-argb-e-controlador",
            "https://www.amazon.com.br/Cooler-Master-MFZ-M2DN-24NP2-R1-Mobius-120P/dp/B0B6Q42TRY/ref=sr_1_5?crid=3RGK8GVHFJ6MX&dib=eyJ2IjoiMSJ9.QB_yJHHCSl36K-mB3YqY5XwOAPfbLZRxI2BPiLnE9aJOzzneIzvVtOljcnZEHglu6F__wsOVlwnGyLGfv4JTi8IzPhvdwCInYaYjO_FBl1y1Gtez5CVf1UaNj_es3a_ZTE-03WZHfpN_rIP9QDRFfvZx1frF4xKyb8ZbBXbKeWT4cZdK5yL0fXzJYYcR4IjmkiUyTmWqLV3X_DrdhXfw_KLyCu_-B2xJtVn1C5qH8hVdcV4B5Sq8vWPGMrNZnOG5TsHQ6SwrdiygF5flCeOFArhU4wwBb9sANtN17Leekj0.iq33NiMGW68VWNs6FsL0wevjRhe4yuXRLtlSTm3MDM4&dib_tag=se&keywords=cooler+master+mobius&qid=1753711185&sprefix=Cooler+Master+Mobius%2Caps%2C458&sr=8-5&ufe=app_do%3Aamzn1.fos.fcd6d665-32ba-4479-9f21-b774e276a678"
        ],
    },
    # 🖥️ Gabinetes brancos ARGB
    {
        "nome": "Lian Li Lancool 215 White",
        "preco_alvo": 499,
        "urls": [
            "https://www.kabum.com.br/produto/346385/gabinete-gamer-lancool-215-2x-fans-argb-laterais-em-vidro-temperado-branco-lancool-215-w-white",
            "https://www.amazon.com.br/Lian-Li-GABINETE-LANCOOL-215/dp/B09MLY1VKC/ref=sr_1_1?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=13NPP8FPZ3JRY&dib=eyJ2IjoiMSJ9.54xEOyJNK6Ous2tY4SvcO0tUfcqCctgF8U9IgZHPqHFGQomO5GvC4hyo02AQxXiZgLrSuWEQcJ4ytmZPCoDB7v6CErGdp8phZGDL2V3FrBJD40Qlt3V2ufWufsADJov8yw8slpywMJl6KgE8-2fLgasJd7UEsCWjpAzZr3YwMWICwuu9IM7Bp32nPBWhpYkInEd6wbfVVqFW3x3EbDwy-kb4qXd1VkAVffzztsCeiPFvR2j7yopXu2PY8WG98ESZyeFQjcllB33mpBGdo3VP6I6rd6_BAYuMskcHzoAj4t4._TmcR7Qkq2-ivLHUGgFJbRvalyPBPpCre6H0vjHA-SQ&dib_tag=se&keywords=Lian+Li+Lancool+215+White&qid=1753711272&sprefix=lian+li+lancool+215+white%2Caps%2C245&sr=8-1&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147"

        ],
    },
    {
        "nome": "Lian Li Lancool 216 White ARGB",
        "preco_alvo": 599,
        "urls": [
            "https://www.kabum.com.br/produto/430153/gabinete-gamer-lancool-216-argb-mid-tower-e-atx-lateral-em-vidro-temperado-3x-cooler-fan-branco-lancool-216rw-white",
            "https://www.amazon.com.br/GABINETE-LANCOOL-BRANCO-FRONTAL-TRASEIRA/dp/B0BN3TTBKM/ref=sr_1_1?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=30X484STXKHHV&dib=eyJ2IjoiMSJ9.E53Nr8j33hbXjLzxBkiFIKal879cffSEIWeX0s0FEAzfJ0Sb1wVP-DX97ZZgbBsxi6jLnUOTJiQuhJ5Iq6bR8zGqX-8dglqNKVBLZIng7xoK_KvsEzo0ZDOf08bNUlLqHFrMTPOkrcMwKOKE8IPmtNkct6jqXT16c26mgKFm5QxIhGldjNHmVuuaTYGtFwmKTuvJmZHz-RWfzHkD0_zg3oRl9nCGlui4HXkBEufq__-rR8w0vJPWG-caQCEZGyWqBgpKZLq97gHr0qeOLy0gofiTjxkRATavI8bKqDjz4lU.xr7uMwmZRnxiKRmnrk_E37LpwDvqHbtEDniN2tiVvh4&dib_tag=se&keywords=Lian+Li+Lancool+216+White+ARGB&qid=1753711333&sprefix=lian+li+lancool+216+white+argb%2Caps%2C174&sr=8-1&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147"
        ],
    },
    {
        "nome": "NZXT H510 Flow White",
        "preco_alvo": 499,
        "urls": [
            "https://www.kabum.com.br/produto/110027/gabinete-gamer-nzxt-h510-mid-tower-com-fan-lateral-em-vidro-branco-ca-h510b-w1",
            "https://www.amazon.com.br/Gabinete-Gamer-NZXT-Branco-CC-H52FW-01/dp/B0D2MHBXRR/ref=sr_1_2?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=CWW62QO7CF8D&dib=eyJ2IjoiMSJ9.33PLKbdWBooaxAC9FI6HwMc47Lb43vxzh_Hi346_TyawQxLHxB7D7OeUkON0U3WFPb999FZYM7qkJpDab1GmKF1446tMz4fdTQ2DQ7drWQuhXVrVs4F02Nl3K9iuhHqdFozcgdc4ZxYAmhMeUZHL1E1IHB9AdM1MwJm6ItB5XA1pmE7xZMfrLzXIVXWHB-Qi-VquP_19rD6p_OQUiNHpu5OtaDSSgVz2b-WG56IZ6VjBZ0A-JJngJmiGCG2x6HVhUDnEOV4dCjazL_qOthzhvTQq-XgoFQ6UOHm2rEjKy-4.2dZ2yzn7elaNaL04umN7-3dnHPDihasH5R_-xz5yV24&dib_tag=se&keywords=NZXT+H510+Flow+White&qid=1753711405&sprefix=nzxt+h510+flow+white%2Caps%2C2807&sr=8-2&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147"
        ],
    },
    {
        "nome": "Corsair 4000D Airflow White",
        "preco_alvo": 499,
        "urls": [
            "https://www.kabum.com.br/produto/657436/gabinete-gamer-corsair-4000d-rs-argb-mid-tower-lateral-em-vidro-com-3x-fans-rs-argb-branco-cc-9011297-ww",
            "https://www.amazon.com.br/Gabinete-Atx-Mid-Tower-Cc-9011201-Ww/dp/B08C74694Z/ref=sr_1_2?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=C4DOM02M0I6Z&dib=eyJ2IjoiMSJ9.-PkyMX47C9QYffQhowH59xxTFYE2o9ztKg_vp7MRwUSq29j9KI3usrqC38DUoJirhHfVCyGSHO8Lm_sce3O5EUgI9nifTYfm0GiYLgqZq8RvNNw1d2MJZSFVkYwThZbox1TNfWiJoAwTF3iRNG7Y_kTbE1f6Zh4aW9Iw9RgNK6BcATkQ6eueOEP73G2PJriP_AwqUhI6WgcFmMDKiGECnBUBy-IRh9eF7moix1kVbQpyU2y_hg_yFeLeJXZGFDbwFQaHM1hNd-zJKXYNpRV3lxFWr2B5texew9yOFvLk61k.mK1gTCwl6jLoIbtnu6M2wxn_QAJaTDRqu8mps202mm8&dib_tag=se&keywords=Corsair%2B4000D%2BAirflow%2BWhite&qid=1753711523&sprefix=corsair%2B4000d%2Bairflow%2Bwhite%2Caps%2C304&sr=8-2&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147&th=1"
        ],
    },
    # 🌡️ Cooler
    {
        "nome": "Rise Mode Z240 Frost White",
        "preco_alvo": 169,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    # 🖥️ Outros (opcional)
    {
        "nome": "SSD NVMe 1TB Gen3 (Crucial P3, Kingston NV2)",
        "preco_alvo": 289,
        "urls": [
            "https://www.kabum.com.br/produto/272356/ssd-kingston-fury-renegade-1tb-m-2-2280-pcie-4-0-x4-nvme-leitura-7300-mb-s-gravacao-6000-mb-s-compativel-com-ps5-sfyrs-1000g",
            "https://www.amazon.com.br/Kingston-2280-NVMe-SNV3S-2000G/dp/B0DBR6TRZQ/ref=sr_1_6?crid=139FT0JXMBDIL&dib=eyJ2IjoiMSJ9.UrGgJ3Vs5iJFianlOTJcvGJvk11lbcgP5_yyW1aYbW_dImCkZPcnRWXHOA35HhRFuB5w060dYE6o4AmIqr73eQ0rjamBXBEWitdoNz6gk0LmkYGYdTfhmlQgj33v4DuZqmDJK4hy7ve9VZahVh-vKTeSWA-4uwbZpQlaYlduu3p8Zto7B9TB5fZnCRzVTw6Cqnbkxin3ryIY7khS3Sq_xuhjkTju8vnA7TURPlGezKtw4ZcOo6M-g8jFzxJzeo9iCbdqtar5wuZMQpDm2GGY5syQejzYf9_omtziLC_DAp0.tO0aninsecC4nLQD_f39X4YagH-4PWuyNVCRmuYUhlc&dib_tag=se&keywords=nv3+1tb+kingston&qid=1753711597&sprefix=NV3+1%2Caps%2C661&sr=8-6&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147"
        ],
    },
    {
        "nome": "SSD NVMe 1TB Gen4 (Crucial P5 Plus, WD SN770)",
        "preco_alvo": 399,
        "urls": [
            "https://www.kabum.com.br/produto/272356/ssd-kingston-fury-renegade-1tb-m-2-2280-pcie-4-0-x4-nvme-leitura-7300-mb-s-gravacao-6000-mb-s-compativel-com-ps5-sfyrs-1000g",
            "https://www.amazon.com.br/Kingston-2280-NVMe-SNV3S-2000G/dp/B0DBR6TRZQ/ref=sr_1_6?crid=139FT0JXMBDIL&dib=eyJ2IjoiMSJ9.UrGgJ3Vs5iJFianlOTJcvGJvk11lbcgP5_yyW1aYbW_dImCkZPcnRWXHOA35HhRFuB5w060dYE6o4AmIqr73eQ0rjamBXBEWitdoNz6gk0LmkYGYdTfhmlQgj33v4DuZqmDJK4hy7ve9VZahVh-vKTeSWA-4uwbZpQlaYlduu3p8Zto7B9TB5fZnCRzVTw6Cqnbkxin3ryIY7khS3Sq_xuhjkTju8vnA7TURPlGezKtw4ZcOo6M-g8jFzxJzeo9iCbdqtar5wuZMQpDm2GGY5syQejzYf9_omtziLC_DAp0.tO0aninsecC4nLQD_f39X4YagH-4PWuyNVCRmuYUhlc&dib_tag=se&keywords=nv3+1tb+kingston&qid=1753711597&sprefix=NV3+1%2Caps%2C661&sr=8-6&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147",
        ],
    },
]

# =============== FUNÇÕES ASSÍNCRONAS ===============

async def get_price(url: str, client: httpx.AsyncClient) -> float | None:
    """
    Função assíncrona para buscar o preço usando XPath para maior robustez.
    """
    try:
        r = await client.get(url, follow_redirects=True)
        r.raise_for_status()
        tree = html.fromstring(r.content)
        
        xpath_expressions = [
            # XPath vencedor para a KaBuM!
            "//div[.//text()[contains(., 'vista no PIX')]]/h4/text()",
            # Fallbacks para outros sites
            '//span[contains(@class, "a-price")]/text()',      # Amazon
        ]
        
        price_text = None
        for expr in xpath_expressions:
            result = tree.xpath(expr)
            if result:
                price_text = result[0].strip()
                print(f"INFO: Preço encontrado com a expressão XPath: {expr}")
                break
        
        if price_text:
            match = re.search(r'[\d\.,]+', price_text)
            if match:
                price_str = match.group(0)
                price_float = float(price_str.replace(".", "").replace(",", "."))
                return price_float

    except httpx.HTTPStatusError as e:
        print(f"ERRO de status HTTP ao acessar {url}: {repr(e)}")
    except Exception as e:
        print(f"ERRO inesperado ao processar a URL {url}: {repr(e)}")
    
    return None

async def rastrear():
    """
    Função principal de rastreio, executada pelo agendador.
    """
    print(f"--- INICIANDO RASTREIO AGENDADO: {datetime.now().strftime('%d/%m/%Y %H:%M')} ---")
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
    promocao_encontrada = False

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=20) as client:
        for item in itens:
            print(f"--- Verificando item: {item['nome']} ---")
            for url in item["urls"]:
                if "LINK-DO-PRODUTO-AQUI" in url:
                    print(f"AVISO: Pulando URL de exemplo para '{item['nome']}': {url}")
                    continue

                preco = await get_price(url, client)
                
                if preco:
                    print(f"  -> Loja: {url.split('/')[2]} | Preço: R$ {preco:.2f}")
                    sheet.append_row([data_hora, item["nome"], preco, url])
                    
                    if preco <= item["preco_alvo"]:
                        msg = (
                            f"🔥 OPORTUNIDADE! 🔥\n\n"
                            f"Produto: {item['nome']}\n"
                            f"Preço: R$ {preco:.2f} (Alvo: R$ {item['preco_alvo']:.2f})\n\n"
                            f"Link: {url}"
                        )
                        await bot.send_message(chat_id=chat_id, text=msg)
                        print(f"ALERTA ENVIADO para {item['nome']}")
                        promocao_encontrada = True
                else:
                    print(f"  -> Preço não encontrado em: {url}")
                    
                await asyncio.sleep(5)
                
            print("-" * (len(item['nome']) + 22))

    if not promocao_encontrada:
        msg_status = "Nenhuma promoção localizada desta vez 😥"
        await bot.send_message(chat_id=chat_id, text=msg_status)
        print("INFO: Nenhuma promoção encontrada. Mensagem de status enviada ao Telegram.")
        
    print(f"--- RASTREIO AGENDADO FINALIZADO: {datetime.now().strftime('%d/%m/%Y %H:%M')} ---")

# =============== EXECUÇÃO COM AGENDAMENTO SEMANAL ===============
async def main():
    """
    Função principal que configura e inicia o agendador.
    """
    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
    
    # Adiciona a tarefa 'rastrear' para ser executada toda sexta-feira às 22:00
    scheduler.add_job(rastrear, 'cron', day_of_week='fri', hour=22)
    
    scheduler.start()
    
    print("✅ Agendador iniciado com sucesso!")
    print("O rastreio será executado automaticamente toda sexta-feira às 22:00.")
    print("Mantenha este terminal aberto para o agendador funcionar.")
    print("Pressione Ctrl+C para finalizar o programa.")
    
    # Mantém o script vivo para que o agendador possa rodar
    try:
        while True:
            await asyncio.sleep(3600) # Mantém o programa ativo, verificando a cada hora.
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("\nAgendador finalizado.")

if __name__ == "__main__":
    # O ponto de entrada agora chama a função 'main', que controla o agendamento
    asyncio.run(main())