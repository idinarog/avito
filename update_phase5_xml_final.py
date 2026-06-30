#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Финальный генератор XML-фида для автозагрузки Avito.
Генерирует XML с меткой времени и копирует в avito_feed.xml.
"""

import sys
import shutil
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database.models import DatabaseManager, Item, Project


class AvitoXmlFeedGenerator:
    CITY_MAP = {
        'MSK': 'Москва', 'KLG': 'Калуга', 'RZN': 'Рязань',
        'TUL': 'Тула', 'NN': 'Нижний Новгород', 'SRN': 'Саранск',
        'LPK': 'Липецк', 'ORL': 'Орел', 'VRN': 'Воронеж',
        'VLD': 'Владимир', 'TVR': 'Тверь', 'KRS': 'Калуга'
    }
    CITY_ORDER = ['Москва','Рязань','Тула','Калуга','Нижний Новгород','Саранск','Липецк','Орел','Воронеж','Владимир','Тверь']
    
    def __init__(self, db_path="avito_commander.db"):
        self.db = DatabaseManager(db_path)
        self.db.init_db()
        self.contact_phone = "+74952921880"
        self.manager_name = "Теплый дом"
        self.image_base_url = "https://ee1c563e-8a5a-42cd-8b8a-5120e056f928.selstorage.ru/"
        self.category = "Ремонт и строительство"
        self.goods_type = "Стройматериалы"
        self.goods_sub_type = "Изоляция"
        self.product_sub_type = "Другое"
        self.condition = "Новое"
        self.ad_type = "Товар от производителя"
    
    def generate_feed(self, project_id: int, output_file: str = None) -> str:
        session = self.db.get_session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise ValueError(f"Проект с ID {project_id} не найден")
            items = session.query(Item).filter(Item.project_id == project_id, Item.is_active == True).all()
            if not items:
                print(f"⚠️ В проекте '{project.name}' нет активных объявлений")
                return ""
            grouped = self._group_by_city(items)
            root = ET.Element("Ads", formatVersion="3", target="Avito.ru")
            total_ads = 0
            for city in self.CITY_ORDER:
                if city in grouped:
                    root.append(ET.Comment(f" {city} "))
                    for idx, item in enumerate(grouped[city], 1):
                        root.append(ET.Comment(f" {idx} "))
                        ad = self._create_ad_element(root, item, city)
                        total_ads += 1
            for city, city_items in grouped.items():
                if city not in self.CITY_ORDER:
                    root.append(ET.Comment(f" {city} "))
                    for idx, item in enumerate(city_items, 1):
                        root.append(ET.Comment(f" {idx} "))
                        ad = self._create_ad_element(root, item, city)
                        total_ads += 1
            xml_str = self._pretty_xml(root)
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(xml_str)
                print(f"✅ XML-фид сохранен: {output_file}")
                print(f"📊 Всего объявлений: {total_ads}")
                # Сохраняем копию как avito_feed.xml
                permanent_file = "avito_feed.xml"
                shutil.copy2(output_file, permanent_file)
                print(f"✅ Постоянная копия сохранена как: {permanent_file}")
            return xml_str
        except Exception as e:
            print(f"❌ Ошибка генерации XML: {e}")
            return ""
        finally:
            session.close()
    
    def _group_by_city(self, items):
        grouped = {}
        for item in items:
            city = self._extract_city(item)
            grouped.setdefault(city, []).append(item)
        return grouped
    
    def _extract_city(self, item):
        if item.item_id_avito and '-' in item.item_id_avito:
            parts = item.item_id_avito.split('-')
            if len(parts) >= 4:
                city_code = parts[-1]
                if city_code in self.CITY_MAP:
                    return self.CITY_MAP[city_code]
        return 'Москва'
    
    def _extract_model(self, item):
        if item.item_id_avito:
            parts = item.item_id_avito.split('-')
            if len(parts) >= 3:
                return '-'.join(parts[1:4])
        return "NF-303"
    
    def _get_price(self, item, city):
        if item.price and item.price > 0:
            return item.price
        price_map = {'Москва':260,'Калуга':330,'Рязань':330,'Тула':330,'Нижний Новгород':330,'Саранск':330,'Липецк':330,'Орел':330,'Воронеж':330,'Владимир':330,'Тверь':330}
        return price_map.get(city, 330)
    
    def _create_ad_element(self, root, item, city):
        ad = ET.SubElement(root, "Ad")
        ET.SubElement(ad, "Id").text = str(item.item_id_avito or f"ID-{item.id}")
        title = item.title or f"Компоненты ППУ {self._extract_model(item)}"
        ET.SubElement(ad, "Title").text = title
        ET.SubElement(ad, "Category").text = self.category
        ET.SubElement(ad, "GoodsType").text = self.goods_type
        ET.SubElement(ad, "GoodsSubType").text = self.goods_sub_type
        ET.SubElement(ad, "ProductSubType").text = self.product_sub_type
        ET.SubElement(ad, "Condition").text = self.condition
        ET.SubElement(ad, "AdType").text = self.ad_type
        ET.SubElement(ad, "Region").text = city
        ET.SubElement(ad, "Address").text = city
        desc = ET.SubElement(ad, "Description")
        desc.text = self._format_description(item, city)
        price = self._get_price(item, city)
        ET.SubElement(ad, "Price").text = str(price)
        images = ET.SubElement(ad, "Images")
        model = self._extract_model(item)
        image_url = f"{self.image_base_url}{model}.jpg"
        ET.SubElement(images, "Image", url=image_url)
        ET.SubElement(ad, "ContactPhone").text = self.contact_phone
        ET.SubElement(ad, "ManagerName").text = self.manager_name
        return ad
    
    def _format_description(self, item, city):
        if item.description and len(item.description) > 50:
            return item.description
        model = self._extract_model(item)
        price = self._get_price(item, city)
        return f"""
Компоненты ППУ РПК {model} — профессиональная система для получения жесткого пенополиуретана (ППУ) методом напыления.

Цена: {price} руб/кг • 15 лет поставок • Отгрузка в день оплаты

Применение:
— утепление фасадов и кровель
— теплоизоляция промышленных объектов
— напыление ППУ в холодильных камерах

Преимущества:
— теплопроводность 0,021–0,024 Вт/(м·°С)
— закрытоячеистая структура
— высокая механическая прочность
— класс горючести Г3

Технические характеристики:
Соотношение компонентов: 100:100
Плотность: 25–29 кг/м³

Склад: Московская область
Доставка — {city} и область.
"""
    
    def _pretty_xml(self, element):
        rough = ET.tostring(element, 'utf-8')
        reparsed = minidom.parseString(rough)
        return reparsed.toprettyxml(indent="  ")


if __name__ == "__main__":
    from database.models import Project
    db = DatabaseManager()
    db.init_db()
    session = db.get_session()
    project = session.query(Project).first()
    if not project:
        print("❌ Нет проектов в БД. Сначала создайте проект.")
        sys.exit(1)
    gen = AvitoXmlFeedGenerator()
    output = f"avito_feed_{project.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
    gen.generate_feed(project.id, output)