package org.example;

import com.itextpdf.kernel.colors.Color;
import com.itextpdf.kernel.colors.ColorConstants;
import com.itextpdf.kernel.geom.PageSize;
import com.itextpdf.kernel.pdf.PdfDocument;
import com.itextpdf.kernel.pdf.PdfWriter;
import com.itextpdf.kernel.pdf.canvas.PdfCanvas;
import com.itextpdf.layout.Document;
import com.itextpdf.layout.element.Cell;
import com.itextpdf.layout.element.Paragraph;
import com.itextpdf.layout.element.Table;
import com.itextpdf.layout.properties.TextAlignment;
import com.itextpdf.layout.renderer.DocumentRenderer;
import com.itextpdf.kernel.geom.Rectangle;
import com.itextpdf.layout.Canvas;

import java.awt.color.ColorSpace;
import java.net.URL;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

public class Main {
    public static void main(String[] args) {

        try {
            Connection connection = null;

            // Creating a database connection
            URL dbResource = Main.class.getClassLoader().getResource("data.db");
            if (dbResource == null) {
                throw new IllegalArgumentException("Database file not found!");
            }
            String dbUrl = "jdbc:sqlite:" + dbResource.getFile();
            connection = DriverManager.getConnection(dbUrl);

            Statement statement = connection.createStatement();
            statement.setQueryTimeout(30);  // set timeout to 30 sec.

            ResultSet rs = statement.executeQuery("SELECT * FROM capitals ORDER BY \"Country\"");

            // Creating a PdfWriter
            PdfWriter writer = new PdfWriter("output.pdf");

            // Creating a PdfDocument
            PdfDocument pdfDoc = new PdfDocument(writer);

            // Creating a Document
            Document document = new Document(pdfDoc, PageSize.LETTER, false);

            // Adding Header
            Paragraph header = new Paragraph("World Capital Cities");
            header.setTextAlignment(TextAlignment.CENTER);
            header.setFontSize(20);
            header.setBold();

            document.add(header);

            // Adding Description
            Paragraph description = new Paragraph("Percent \"%\" is city population as a percentage of the country, as of \"Year\"");
            description.setTextAlignment(TextAlignment.LEFT);
            description.setFontSize(12);
            description.setItalic();

            document.add(description);

            // Creating a table
            float [] pointColumnWidths = {200F, 150F, 50f, 50f, 50f};
            Table table = new Table(pointColumnWidths);
            table.setWidth(540f);

            // Adding header cells to the table
            table.addHeaderCell(new Cell().add(new Paragraph("Country")).setBold().setBorder(null));
            table.addHeaderCell(new Cell().add(new Paragraph("Capital")).setBold().setBorder(null));
            table.addHeaderCell(new Cell().add(new Paragraph("Population")).setBold().setBorder(null));
            table.addHeaderCell(new Cell().add(new Paragraph("%")).setBold().setBorder(null));
            table.addHeaderCell(new Cell().add(new Paragraph("Year")).setBold().setBorder(null));

            // Adding cells to the table
            int index = 0;
            Color backColor;
            while(rs.next()) {
                if (index % 2 == 0)
                    backColor = ColorConstants.LIGHT_GRAY;
                else
                    backColor = ColorConstants.WHITE;

                table.addCell(new Cell().add(new Paragraph(rs.getString("Country"))).setBackgroundColor(backColor));
                table.addCell(new Cell().add(new Paragraph(rs.getString("Capital"))).setBackgroundColor(backColor));
                table.addCell(new Cell().add(new Paragraph(rs.getString("Population"))).setBackgroundColor(backColor));
                table.addCell(new Cell().add(new Paragraph(rs.getString("Percent"))).setBackgroundColor(backColor));
                table.addCell(new Cell().add(new Paragraph(rs.getString("Year"))).setBackgroundColor(backColor));

                index += 1;
            }

            // Adding Table to document
            document.add(table);

            // total page number
            int total = ((DocumentRenderer)document.getRenderer()).getCurrentArea().getPageNumber();
            PdfCanvas pdfCanvas;

            for (int i = 1; i <= total; i++) {
                // Create a new page
                Rectangle pageSize = pdfDoc.getPage(i).getPageSize();
                pdfCanvas = new PdfCanvas(pdfDoc.getPage(i));

                // Add the header and footer
                Canvas canvas = new Canvas(pdfCanvas, pageSize, true);
                canvas.setFontSize(12);

                // Write text at position
                // Core Java Volume II
                canvas.showTextAligned(String.format("World Capital Cities, Page %s of %s", i, total), (pageSize.getLeft() + pageSize.getRight()) / 2,
                        pageSize.getBottom() + 12f, TextAlignment.CENTER, 0);
            }

            document.close();

            if(connection != null) {
                connection.close();
            }

        } catch(Exception e) {
            e.printStackTrace();
        }
    }
}