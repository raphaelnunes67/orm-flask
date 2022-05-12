from array import array
from multiprocessing.dummy import Array
from flask import send_file, after_this_request, request
from flask_restful import Resource, reqparse
from models.sysinfo import SysInfoModel
from flask_jwt_extended import jwt_required
from xlsxwriter import Workbook
import csv
from os import remove, listdir
from os.path import getsize

class SysInfo(Resource):
    attributes = reqparse.RequestParser()
    attributes.add_argument('model', type=str, required=True, help="The field 'model' cannot be left blank.")
    attributes.add_argument('quantity', type=int, required=True)
    attributes.add_argument('work_order', type=str, required=True)
    attributes.add_argument('created_at', type=str, required=True)
    attributes.add_argument('details', type=str, required=True)

    def get(self, id):
        sysinfo = SysInfoModel.find_sysinfo(id)
        if sysinfo:
            return sysinfo.json()
        return {'message': 'Information not found.'}, 404

    # @jwt_required
    # def post(self, id):
    #     if SysInfoModel.find_sysinfo(id):
    #         return {"message": "Information id '{}' already exists.".format(id)}, 400 # Bad Request

    #     data = SysInfo.attributes.parse_args()
    #     sysinfo = SysInfoModel(id,**data)
    #     try:
    #         sysinfo.save_sysinfo()
    #     except:
    #         return {"message": "An error ocurred trying to create information."}, 500 # Internal Server Error
    #     return sysinfo.json(), 201

    @jwt_required
    def put(self, id):
        data = SysInfo.attributes.parse_args()
        sysinfo = SysInfoModel(id, **data)

        sysinfo_found = SysInfoModel.find_sysinfo(id)
        if sysinfo_found:
            sysinfo_found.update_sysinfo(id, **data)
            sysinfo_found.save_sysinfo()
            return sysinfo_found.json(), 200
        sysinfo.save_sysinfo()
        return sysinfo.json(), 201

    @jwt_required
    def delete(self, id):
        sysinfo = SysInfoModel.find_sysinfo(id)
        if sysinfo:
            sysinfo.delete_sysinfo()
            return {'message': 'Information deleted.'}, 200
        return {'message': 'Information not found.'}, 404


class SysInfos(Resource):
    
    attributes = reqparse.RequestParser()
    attributes.add_argument('model', type=str, required=True, help="The field 'model' cannot be left blank.")
    attributes.add_argument('quantity', type=int, required=True)
    attributes.add_argument('work_order', type=str, required=True)
    attributes.add_argument('created_at', type=str, required=True)
    attributes.add_argument('details', type=str, required=True)
    
    @jwt_required
    def post(self):
        @after_this_request
        def handle_database_size(response):
            if getsize('data/database.db') > 734003200: #20480
                id = SysInfoModel.first_sysinfo()
                sysinfo = SysInfoModel.find_sysinfo(id)
                if sysinfo:
                    sysinfo.delete_sysinfo()           
                    
            return response
        
        data = SysInfos.attributes.parse_args()
        sysinfo = SysInfoModel(**data)
        try:
            sysinfo.save_sysinfo()
        except:
            return {"message": "An error ocurred trying to create information."}, 500 #Internal Server Error
        return sysinfo.json(), 201
    
    @jwt_required
    def delete(self):
        last_id = SysInfoModel.last_sysinfo()
        for id in range(last_id+1):
            sysinfo = SysInfoModel.find_sysinfo(id)
            if sysinfo:
                sysinfo.delete_sysinfo()
        return {'message': 'All data deleted.'}, 200
            
            
class SysInfosTable(Resource):
   
    def get(self):
        
        from_date_time = request.args.get('from_date_time', default=None, type=str)
        to_date_time = request.args.get('to_date_time', default=None, type=str)
        model = request.args.get('model', default=None, type=str)
        page = request.args.get('page', default=None, type=str)
        data_per_page = 50
        
        try:
            duts = SysInfoModel.filter_results(from_date_time, to_date_time, model)
            
            n_results = 0            
            for entry in duts:            
                n_results +=1
                
            if n_results == 0:
                return  {'message': 'This data do not exists'}, 400
                
            n_pages =  n_results / data_per_page
            if n_pages - int(n_pages) > 0:
                n_pages = int(n_pages) + 1
                
            values = []
            
            if page == None:          
                if n_pages == 1:
                    for entry in duts:
                        values.append({
                            'id': entry.id,
                            'model': entry.model,
                            'quantity': entry.quantity,
                            'work_order': entry.work_order,
                            'created_at': entry.created_at.isoformat(),
                            'details': entry.details
                        })
                        
                    return {'values':values, 'page': None}, 200
                
                else:
                    for entry in duts:
                        values.append({
                            'id': entry.id,
                            'model': entry.model,
                            'quantity': entry.quantity,
                            'work_order': entry.work_order,
                            'created_at': entry.created_at.isoformat(),
                            'details': entry.details
                        })
                        
                        if len(values) == data_per_page:
                            return {'values':values, 'page': 1, 'n_pages': n_pages }, 200        
                        
            else:
                page = int(page)
                  
                if page == 0 or page > n_pages:
                    return  {'message': 'This page do not exists'}, 400
                
                print (page)
                begin_item = (page * data_per_page) - data_per_page
                last_item = (page * data_per_page) - 1
                count = 0
                for entry in duts:
                    if count >= begin_item and count <= last_item:
                        try:
                            values.append({
                                'id': entry.id,
                                'model': entry.model,
                                'quantity': entry.quantity,
                                'work_order': entry.work_order,
                                'created_at': entry.created_at.isoformat(),
                                'details': entry.details
                            })
                        except:
                            break
                        
                    if count > last_item:
                        break
                
                    count +=1
                        
                return {'values':values, 'page': page, 'n_pages': n_pages }, 200
        except:
             return {"message": "An error ocurred trying to create information."}, 500 # Internal Server Error 
        
    
class SysInfosExport(Resource):
    attributes = reqparse.RequestParser()
    attributes.add_argument('from', type=str, required=True)
    attributes.add_argument('to', type=str, required=True)
    attributes.add_argument('model', type=str, required=True)
    attributes.add_argument('file_type', type=str, required=True)
    
    @jwt_required
    def post(self):
        try:
            data = SysInfosExport.attributes.parse_args() 
            from_date_time  = data['from']
            to_date_time = data['to']
            model = data['model']
            file_type = data['file_type']
            duts = SysInfoModel.filter_results(from_date_time, to_date_time, model)
            matrix = []
            matrix.append(['id', 'quantity', 'work_order', 'created_at', 'details'])
            for entry in duts:
                row = [entry.id, entry.quantity, entry.work_order, entry.created_at.isoformat(), entry.details]
                matrix.append(row)
            
            if file_type == "xlsx":
                workbook = Workbook('data/damper_export.xlsx')
                worksheet = workbook.add_worksheet()
                for row, data in enumerate(matrix):
                    worksheet.write_row(row, 0, data)
                workbook.close()
            elif file_type == "csv":
                with open('data/damper_export.csv', 'w') as csv_file:
                    writer = csv.writer(csv_file)
                    for row in matrix:
                        writer.writerow(row)
            else:
                 return {"message": "An error ocurred trying to create information."}, 400 
                
            
            @after_this_request
            def remove_file(response):
                try:
                    files = listdir('data/')
                    file_name = [(file) for file in files if file.find("damper_export") != -1][0]
                    remove(f'data/{file_name}')
                except:
                    pass
            
                return response
                
            return send_file('data/damper_export.' + file_type, as_attachment=True)
        except:
            return {"message": "An error ocurred trying to create information."}, 500 # Internal Server Error

class SysInfoClean(Resource):
    attributes = reqparse.RequestParser()
    attributes.add_argument('ids', action='append', type=int, required=True)
    
    @jwt_required
    def post(self):
        ids = self.attributes.parse_args()
        print(ids)
        for id in ids:
            sysinfo = SysInfoModel.find_sysinfo(id)
            if sysinfo:
                SysInfo.query.filter(SysInfo.id._in(ids)).delete()
                sysinfo.delete_sysinfo()
                
        
        return {'message': 'Information deleted.'}, 200
            