package org.example;

import com.itextpdf.io.image.ImageData;
import com.itextpdf.io.image.ImageDataFactory;
import com.itextpdf.kernel.colors.Color;
import com.itextpdf.kernel.colors.ColorConstants;
import com.itextpdf.kernel.geom.PageSize;
import com.itextpdf.kernel.pdf.PdfDocument;
import com.itextpdf.kernel.pdf.PdfWriter;
import com.itextpdf.layout.Document;
import com.itextpdf.layout.properties.TextAlignment;
import com.itextpdf.layout.element.Cell;
import com.itextpdf.layout.element.Image;
import com.itextpdf.layout.element.Paragraph;
import com.itextpdf.layout.element.Table;
import com.itextpdf.layout.properties.HorizontalAlignment;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

public class NatoMembers {
    public static String data = "Belgium;Founder;Belgium.jpg;1949\n" +
            "Denmark;Founder;Denmark.jpg;1949\n" +
            "France;Founder;France.jpg;1949\n" +
            "Iceland;Founder;Iceland.jpg;1949\n" +
            "Italy;Founder;Italy.jpg;1949\n" +
            "Canada;Founder;Canada.jpg;1949\n" +
            "Luxembourg;Founder;Luxembourg.jpg;1949\n" +
            "Netherlands;Founder;Netherlands.jpg;1949\n" +
            "Norway;Founder;Norway.jpg;1949\n" +
            "Portugal;Founder;Portugal.jpg;1949\n" +
            "United Kingdom;Founder;United_Kingdom.jpg;1949\n" +
            "United States;Founder;United_States.jpg;1949\n" +
            "Greece;Joiner;Greece.jpg;1952\n" +
            "Turkey;Joiner;Turkey.jpg;1952\n" +
            "Germany;Joiner;Germany.jpg;1955\n" +
            "Spain;Joiner;Spain.jpg;1982\n" +
            "Poland;Joiner;Poland.jpg;1999\n" +
            "Czech Republic;Joiner;Czech_Republic.jpg;1999\n" +
            "Hungary;Joiner;Hungary.jpg;1999\n" +
            "Bulgaria;Joiner;Bulgaria.jpg;2004\n" +
            "Estonia;Joiner;Estonia.jpg;2004\n" +
            "Latvia;Joiner;Latvia.jpg;2004\n" +
            "Lithuania;Joiner;Lithuania.jpg;2004\n" +
            "Romania;Joiner;Romania.jpg;2004\n" +
            "Slovakia;Joiner;Slovakia.jpg;2004\n" +
            "Slovenia;Joiner;Slovenia.jpg;2004\n" +
            "Albania;Joiner;Albania.jpg;2009\n" +
            "Croatia;Joiner;Croatia.jpg;2009\n" +
            "Montenegro;Joiner;Montenegro.jpg;2017\n" +
            "North Macedonia;Joiner;North_Macedonia.jpg;2020\n" +
            "Finland;Joiner;Finland.jpg;2023\n" +
            "Sweden;Observer;Sweden.jpg;N/A";

    public static void main(String[] args) throws IOException {
        Color backColor;
        float tableWidth = 320f;
        float[] pointColumnWidths = {200f, 150f, 50f, 50f};
        String[] columns = {"Country", "Type", "Flag", "Since"};
        int numColumn = 4;

        ZipFile zipFile = new ZipFile("src/main/resources/national-flags.zip");

        PdfWriter writer = new PdfWriter("nato_members.pdf");

        // Creating a PdfDocument
        PdfDocument pdfDoc = new PdfDocument(writer);

        // Creating a Document
        Document document = new Document(pdfDoc, PageSize.LETTER, false);

        // Adding header
        Paragraph header = new Paragraph("Members of the NATO");
        header.setTextAlignment(TextAlignment.CENTER);
        header.setFontSize(20);
        header.setBold();

        document.add(header);

        // Initialize table
        Table table = new Table(pointColumnWidths);
        table.setWidth(tableWidth);
        table.setHorizontalAlignment(HorizontalAlignment.CENTER);

        // Adding header cells to the table
        for (int i =0; i <numColumn ; i ++) {
            table.addHeaderCell(new Cell().add(new Paragraph(columns[i])).setBold().setBorder(null));
        }

        // Adding cells to the table
        String[] rows = data.split("\n");

        for (int i =0; i < rows.length; i++) {
            if (i % 2 == 0)
                backColor = ColorConstants.LIGHT_GRAY;
            else
                backColor = ColorConstants.WHITE;

            String[] values = rows[i].split(";");

            ZipEntry entry = zipFile.getEntry(values[2]);

            if(entry != null) {
                InputStream stream = zipFile.getInputStream(entry);

                // Read the stream and then close it
                byte[] bytes = readStream(stream);
                stream.close();

                // Convert byte array to ImageData
                ImageData imageData = ImageDataFactory.create(bytes);

                // Now, use imageData object wherever you need
                for (int j = 0; j < values.length; j++) {
                    if (j == 2)
                        table.addCell(new Cell().add(new Image(imageData)).setBackgroundColor(backColor).setBorder(null));
                    else
                        table.addCell(new Cell().add(new Paragraph(values[j])).setBackgroundColor(backColor).setBorder(null));
                }
            }
        }

        document.add(table);

        document.close();
    }

    public static byte[] readStream(InputStream input) throws IOException {
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        byte[] buffer = new byte[4096];
        int n;
        while ((n = input.read(buffer)) != -1) {
            output.write(buffer, 0, n);
        }
        return output.toByteArray();
    }
}
