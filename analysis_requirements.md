## Chẩn đoán và đánh giá bệnh nhân
### Retrieve hình ảnh MRI/CT/X-ray theo bệnh nhân hoặc vùng cơ thể
  - Ví dụ: Lấy tất cả MRI cột sống thắt lưng của bệnh nhân nam 53 tuổi có triệu chứng đau lưng.
  - Mục đích: So sánh các hình ảnh theo thời gian để đánh giá tiến triển thoái hóa hoặc tổn thương đĩa đệm.
### Kết hợp hình ảnh với ghi chú lâm sàng
  - Ví dụ: Truy xuất hình ảnh L4-L5 kèm theo ghi chú “degenerative annular disc bulge… compressing left nerve root”.
  - Mục đích: Hỗ trợ bác sĩ xác định chính xác vị trí và mức độ tổn thương, từ đó lên kế hoạch điều trị.
### Tìm kiếm mẫu bệnh lý tương tự (Pattern Matching)
  - Ví dụ: Tìm các bệnh nhân khác có “annular tear” hoặc “nerve root compression” trên L4-L5.
  - Mục đích: Học hỏi từ các ca điều trị trước, dự đoán nguy cơ biến chứng.

## Quản lý và theo dõi tiến triển bệnh
### So sánh hình ảnh theo thời gian
  - Retrieve chuỗi hình ảnh của một bệnh nhân qua các lần MRI.
  - Mục đích: Xem tiến triển thoái hóa, mức độ sưng viêm, hiệu quả của thuốc hoặc vật lý trị liệu.
### Theo dõi triệu chứng kết hợp hình ảnh
  - Retrieve ghi chú lâm sàng + hình ảnh từ các lần khám gần nhất.
  - Mục đích: Đánh giá sự cải thiện hoặc xấu đi của tình trạng “disc bulge” hoặc “nerve compression”.

## Hỗ trợ quyết định điều trị
### Truy xuất dữ liệu để lập kế hoạch phẫu thuật
  - Ví dụ: MRI L4-L5 + thông tin về “compressing left nerve root” giúp bác sĩ lựa chọn kỹ thuật phẫu thuật phù hợp (microdiscectomy, laminectomy).
### Predictive analytics
  - Dựa vào dữ liệu hình ảnh + triệu chứng + lịch sử bệnh nhân để dự đoán nguy cơ thoát vị đĩa đệm hoặc đau thần kinh tọa.

## Nghiên cứu và học thuật
### Tạo dataset cho AI/ML trong chẩn đoán
  - Retrieve các DICOM + ghi chú bác sĩ để huấn luyện mô hình phát hiện “annular disc bulge”, “nerve compression”.
### So sánh kỹ thuật điều trị
  - Retrieve dữ liệu hình ảnh của các ca đã được phẫu thuật hoặc điều trị bảo tồn, đánh giá hiệu quả.

## Quản lý và chuẩn hóa dữ liệu y tế
### Kiểm tra chất lượng hình ảnh
  - Retrieve metadata DICOM (slice thickness, magnetic field strength, orientation) để đảm bảo hình ảnh đủ chuẩn cho chẩn đoán.
### Theo dõi bệnh nhân theo chỉ số sinh lý
  - Kết hợp kích thước, cân nặng, tuổi tác, và metadata MRI để chuẩn hóa protocol chụp.

## Telemedicine và tham vấn từ xa
### Retrieve hình ảnh + báo cáo lâm sàng để gửi cho bác sĩ chuyên khoa từ xa.
### Hỗ trợ đưa ra chẩn đoán thứ hai hoặc hội chẩn đa chuyên khoa.
