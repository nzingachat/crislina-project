#!/usr/bin/env python3
"""
Script de Inicialização da Base de Dados - MVP do Projecto CrisLina

Este script cria e popula a base de dados para o Mínimo Produto Viável (MVP)
do sistema de gestão de frota inteligente CrisLina.

O objetivo deste MVP é estabelecer a fundação de dados necessária para
suportar os futuros módulos de RFID, IoT e Manutenção Preditiva com IA,
utilizando um cenário de dados totalmente localizado para Angola.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, date, timedelta
from src.models import db, User, Vehicle, Driver, Trip, Maintenance
from flask import Flask

def create_app():
    """Cria e configura uma instância da aplicação Flask para interagir com a DB."""
    app = Flask(__name__)
    # O caminho para a base de dados é relativo à localização deste script
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True) # Garante que o diretório 'database' existe
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'uma_chave_secreta_para_o_projecto_crislina'
    db.init_app(app)
    return app

def init_database():
    """
    Inicializa a base de dados: apaga tabelas existentes, cria a nova estrutura
    e popula com dados de exemplo para o cenário angolano.
    """
    app = create_app()
    
    with app.app_context():
        # Apaga todas as tabelas e recria a estrutura a partir dos modelos definidos
        db.drop_all()
        db.create_all()
        
        # --- Criação de Utilizadores com diferentes perfis ---
        # (Admin, Gestor, Motorista) como previsto na arquitetura do sistema
        admin = User(username='admin', email='admin@crislina.co.ao', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        
        manager = User(username='manager', email='gestor@crislina.co.ao', role='manager')
        manager.set_password('gestor123')
        db.session.add(manager)
        
        driver_user = User(username='driver1', email='motorista1@crislina.co.ao', role='driver')
        driver_user.set_password('motorista123')
        db.session.add(driver_user)
        
        # --- Criação da Frota de Veículos ---
        # Dados localizados para Angola (modelos e matrículas)
        vehicles = [
            Vehicle(reg_no='LD-12-34-AB', model='Toyota Hilux', fuel_type='gasóleo', status='active'),
            Vehicle(reg_no='BE-56-78-CD', model='Ford Ranger', fuel_type='gasóleo', status='active'),
            Vehicle(reg_no='LA-90-12-EF', model='Kia Rio', fuel_type='gasolina', status='active'),
            Vehicle(reg_no='LU-34-56-GH', model='Hyundai i10', fuel_type='gasolina', status='maintenance'),
            Vehicle(reg_no='CA-78-90-IJ', model='Suzuki Swift', fuel_type='gasolina', status='active')
        ]
        db.session.add_all(vehicles)
        
        # --- Criação de Motoristas ---
        # Nomes e contactos para o cenário angolano
        drivers = [
            Driver(name='João Silva', license_no='008162537KS046', phone='+244923123456', email='joao.silva@exemplo.co.ao', user_id=3),
            Driver(name='Ana Pereira', license_no='003172516KS012', phone='+244924567890', email='ana.pereira@exemplo.co.ao'),
            Driver(name='Carlos Santos', license_no='004162511KS007', phone='+244925987654', email='carlos.santos@exemplo.co.ao'),
            Driver(name='Maria Costa', license_no='009162642KS044', phone='+244926112233', email='maria.costa@exemplo.co.ao')
        ]
        db.session.add_all(drivers)
        
        # Commit para garantir que Veículos e Motoristas tenham IDs antes de criar as Viagens
        db.session.commit()
        
        # --- Criação de Viagens ---
        # Rotas entre cidades de Angola para simular operações reais
        base_date = date.today() - timedelta(days=30)
        trips = [
            Trip(vehicle_id=1, driver_id=1, source='Luanda', destination='Soyo', 
                 distance=450.0, fuel_used=42.5, trip_date=base_date, status='completed'),
            Trip(vehicle_id=2, driver_id=2, source='Benguela', destination='Lubango', 
                 distance=300.0, fuel_used=31.0, trip_date=base_date + timedelta(days=1), status='completed'),
            Trip(vehicle_id=3, driver_id=3, source='Huambo', destination='Luanda', 
                 distance=600.0, fuel_used=35.5, trip_date=base_date + timedelta(days=2), status='completed'),
            Trip(vehicle_id=1, driver_id=1, source='Soyo', destination='Malanje', 
                 distance=720.0, fuel_used=68.0, trip_date=base_date + timedelta(days=3), status='completed'),
            Trip(vehicle_id=5, driver_id=4, source='Lubango', destination='Namibe', 
                 distance=180.0, fuel_used=11.0, trip_date=base_date + timedelta(days=4), status='completed'),
            Trip(vehicle_id=2, driver_id=2, source='Luanda', destination='Uíge', 
                 distance=350.0, fuel_used=33.0, trip_date=base_date + timedelta(days=5), status='in_progress'),
            Trip(vehicle_id=1, driver_id=1, source='Cabinda', destination='Soyo', 
                 distance=210.0, fuel_used=22.0, trip_date=date.today(), status='planned')
        ]
        db.session.add_all(trips)
        
        # --- Criação de Registos de Manutenção ---
        # Histórico essencial para o futuro módulo de manutenção preditiva (IA)
        maintenance_records = [
            Maintenance(vehicle_id=1, date=base_date - timedelta(days=10), cost=25000.0, 
                       description='Mudança de óleo e substituição de filtros (ar e combustível).', maintenance_type='routine'),
            Maintenance(vehicle_id=2, date=base_date - timedelta(days=5), cost=45000.0, 
                       description='Substituição das pastilhas e discos de travão dianteiros.', maintenance_type='repair'),
            Maintenance(vehicle_id=4, date=base_date, cost=150000.0, 
                       description='Reparação da junta do cabeçote do motor.', maintenance_type='emergency'),
            Maintenance(vehicle_id=3, date=base_date - timedelta(days=15), cost=15000.0, 
                       description='Rotação, alinhamento e calibragem de pneus.', maintenance_type='routine', status='in_progress'),
            Maintenance(vehicle_id=1, date=base_date - timedelta(days=20), cost=35000.0, 
                       description='Substituição da bateria e verificação do alternador.', maintenance_type='repair')
        ]
        db.session.add_all(maintenance_records)
        
        # Commit final para salvar todas as alterações
        db.session.commit()
        
        print("="*50)
        print("Base de Dados do Projecto CrisLina inicializada com sucesso!")
        print("="*50)
        print("\nUtilizadores padrão criados:")
        print("  - Admin:     username='admin', password='admin123'")
        print("  - Gestor:    username='gestor', password='gestor123'")
        print("  - Motorista: username='motorista1', password='motorista123'")
        print(f"\nDados de exemplo criados:")
        print(f"  - {len(vehicles)} veículos")
        print(f"  - {len(drivers)} motoristas")
        print(f"  - {len(trips)} viagens")
        print(f"  - {len(maintenance_records)} registos de manutenção")
        print("\nPara iniciar a aplicação, execute o ficheiro principal.")

if __name__ == '__main__':
    init_database()
